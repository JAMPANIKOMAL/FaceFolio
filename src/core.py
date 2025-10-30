import face_recognition
from PIL import Image
import shutil
import zipfile
from pathlib import Path

# --- File System Setup ---
TEMP_DIR = Path("temp_files")
EXTRACTED_EVENTS_DIR = TEMP_DIR / "extracted_events"
EXTRACTED_REFERENCES_DIR = TEMP_DIR / "extracted_references"
UNKNOWN_PORTRAITS_DIR = TEMP_DIR / "unknown_portraits"
OUTPUT_DIR = Path("output")
DOWNLOAD_ZIP_PATH = Path("FaceFolio_Sorted.zip")

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

def setup_directories():
    """Cleans up old files and creates a fresh directory structure."""
    print("--- Setting up directories ---")
    for path in [TEMP_DIR, OUTPUT_DIR]:
        if path.exists():
            shutil.rmtree(path)
    if DOWNLOAD_ZIP_PATH.exists():
        DOWNLOAD_ZIP_PATH.unlink()
        
    for path in [TEMP_DIR, EXTRACTED_EVENTS_DIR, EXTRACTED_REFERENCES_DIR, UNKNOWN_PORTRAITS_DIR, OUTPUT_DIR]:
        path.mkdir(exist_ok=True)
    print("Directories are ready.")

def extract_zip(zip_path, extract_to):
    """Extracts a zip file and returns a list of the extracted image paths."""
    print(f"Extracting '{zip_path}' to '{extract_to}'...")
    image_paths = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                if not member.is_dir() and Path(member.filename).suffix.lower() in IMAGE_EXTENSIONS:
                    extracted_path = extract_to / Path(member.filename).name
                    with zip_ref.open(member) as source, open(extracted_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    image_paths.append(extracted_path)
        print("Extraction complete.")
        return image_paths
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        return []

def _is_image_file(path):
    return path.suffix.lower() in IMAGE_EXTENSIONS

# --- Workflow 1: Reference-Based Sorting ---

def load_reference_encodings(ref_dir):
    """Loads reference images and creates known face encodings."""
    print("--- Loading reference photos ---")
    known_face_encodings = []
    known_face_names = []

    for image_path in ref_dir.rglob('*'):
        if not _is_image_file(image_path):
            continue
        name = image_path.stem
        print(f"Processing reference: {name}")
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(name)
                print(f"  > Found face for {name}.")
            else:
                print(f"  > Warning: No face found in {image_path.name}.")
        except Exception as e:
            print(f"  > Error processing {image_path.name}: {e}")
            
    return known_face_encodings, known_face_names

def find_and_sort_faces_by_reference(progress_callback, image_paths, known_encodings, known_names):
    """Iterates through event photos, finds faces, and sorts them by reference."""
    print("--- Sorting event photos by reference ---")
    total_images = len(image_paths)

    for i, image_path in enumerate(image_paths):
        progress_callback(i + 1, total_images, image_path.name)
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            people_found_in_image = set()
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                if True in matches:
                    name = known_names[matches.index(True)]
                    if name not in people_found_in_image:
                        person_dir = OUTPUT_DIR / name
                        person_dir.mkdir(exist_ok=True)
                        shutil.copy2(image_path, person_dir)
                        people_found_in_image.add(name)
            
            if not people_found_in_image:
                 print(f"  > No known faces found in {image_path.name}.")
        except Exception as e:
            print(f"  > Error processing {image_path.name}: {e}")

def copy_reference_photos(ref_dir):
    """Copies reference photos into their corresponding output folders."""
    print("--- Copying reference photos to output folders ---")
    for image_path in ref_dir.rglob('*'):
        if not _is_image_file(image_path):
            continue
        name = image_path.stem
        person_dir = OUTPUT_DIR / name
        if person_dir.exists():
            shutil.copy2(image_path, person_dir)

# --- Workflow 2: Automatic Discovery ---

def find_unique_faces(progress_callback, image_paths, tolerance=0.6):
    """Analyzes all event photos to discover unique individuals."""
    print("--- Discovering unique faces in event photos ---")
    discovered_encodings = []
    all_face_metadata = []
    total_images = len(image_paths)

    for i, image_path in enumerate(image_paths):
        progress_callback(i + 1, total_images, image_path.name)
        try:
            image_data = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image_data)
            face_encodings = face_recognition.face_encodings(image_data, face_locations)

            if not face_encodings:
                continue

            for j, face_encoding in enumerate(face_encodings):
                all_face_metadata.append({'path': image_path, 'encoding': face_encoding})
                matches = face_recognition.compare_faces(discovered_encodings, face_encoding, tolerance)
                if True not in matches:
                    discovered_encodings.append(face_encoding)
                    _save_portrait(image_path, face_locations[j], len(discovered_encodings) - 1)
        except Exception as e:
            print(f"  > Error processing {image_path.name}: {e}")
            
    print(f"--- Discovery complete. Found {len(discovered_encodings)} unique people. ---")
    return discovered_encodings, all_face_metadata

def _save_portrait(image_path, location, person_index):
    """Helper function to crop and save a face portrait."""
    top, right, bottom, left = location
    image = Image.open(image_path)
    face_image = image.crop((left, top, right, bottom))
    
    padding = 20
    padded_image = Image.new(face_image.mode, (face_image.width + 2*padding, face_image.height + 2*padding), (255, 255, 255, 0))
    padded_image.paste(face_image, (padding, padding))

    portrait_path = UNKNOWN_PORTRAITS_DIR / f"person_{person_index}.png"
    padded_image.save(portrait_path)

def sort_photos_by_discovered_faces(progress_callback, all_face_metadata, discovered_encodings, user_names, tolerance=0.6):
    """Sorts photos based on the names provided by the user."""
    print("--- Sorting photos based on user tags ---")
    name_map = {idx: name for idx, name in user_names.items() if name}
    
    # Use a set to track which photos have been processed to avoid duplicate progress updates
    processed_photos = set()
    total_photos = len(set(meta['path'] for meta in all_face_metadata))
    
    for metadata in all_face_metadata:
        image_path = metadata['path']
        if image_path not in processed_photos:
            progress_callback(len(processed_photos) + 1, total_photos, image_path.name)
            processed_photos.add(image_path)

        face_encoding = metadata['encoding']
        matches = face_recognition.compare_faces(discovered_encodings, face_encoding, tolerance)
        if True in matches:
            match_index = matches.index(True)
            if match_index in name_map:
                name = name_map[match_index]
                person_dir = OUTPUT_DIR / name
                person_dir.mkdir(exist_ok=True)
                if not (person_dir / image_path.name).exists():
                    shutil.copy2(image_path, person_dir)

# --- Finalization ---

def create_download_zip(output_dir, download_path):
    """Creates a final zip file of the sorted output directory."""
    print(f"--- Creating final zip file at '{download_path}' ---")
    try:
        shutil.make_archive(str(download_path.with_suffix('')), 'zip', str(output_dir))
        print("Zip file created successfully.")
    except Exception as e:
        print(f"Error creating zip file: {e}")
