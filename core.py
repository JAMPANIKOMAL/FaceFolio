import face_recognition
from PIL import Image
import shutil
import zipfile
from pathlib import Path

# --- File System Setup ---
# Define the directory structure for the application's temporary and output files.
TEMP_DIR = Path("temp_files")
EXTRACTED_EVENTS_DIR = TEMP_DIR / "extracted_events"
EXTRACTED_REFERENCES_DIR = TEMP_DIR / "extracted_references"
UNKNOWN_PORTRAITS_DIR = TEMP_DIR / "unknown_portraits"
OUTPUT_DIR = Path("output")
DOWNLOAD_ZIP_PATH = Path("FaceFolio_Sorted.zip")

# List of common image file extensions to process.
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

def setup_directories():
    """
    Cleans up old files and creates a fresh directory structure for a new run.
    This ensures that data from previous sessions doesn't interfere with the current one.
    """
    print("--- Setting up directories ---")
    # Clean up previous session's directories
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    if DOWNLOAD_ZIP_PATH.exists():
        DOWNLOAD_ZIP_PATH.unlink()
        
    # Create fresh directories
    TEMP_DIR.mkdir(exist_ok=True)
    EXTRACTED_EVENTS_DIR.mkdir(exist_ok=True)
    EXTRACTED_REFERENCES_DIR.mkdir(exist_ok=True)
    UNKNOWN_PORTRAITS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("Directories are ready.")

def extract_zip(zip_path, extract_to):
    """
    Extracts the contents of a zip file to a specified directory.
    Includes error handling for corrupted or invalid zip files.
    """
    print(f"Extracting '{zip_path}' to '{extract_to}'...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction complete.")
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid zip file or is corrupted.")
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")

def _is_image_file(path):
    """Helper function to check if a file is a supported image type."""
    return path.suffix.lower() in IMAGE_EXTENSIONS

# --- Workflow 1: Reference-Based Sorting ---

def load_reference_encodings(ref_dir):
    """
    Loads reference images, detects faces, and creates known face encodings.
    The person's name is derived from the image filename (e.g., 'Alice.jpg').
    """
    print("--- Loading reference photos ---")
    known_face_encodings = []
    known_face_names = []

    for image_path in ref_dir.rglob('*'):
        if not _is_image_file(image_path):
            continue

        name = image_path.stem  # Get filename without extension
        print(f"Processing reference: {name}")

        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                # Use the first face found in the reference image
                known_face_encodings.append(encodings[0])
                known_face_names.append(name)
                print(f"  > Found face for {name}.")
            else:
                print(f"  > Warning: No face found in {image_path.name}.")
        except Exception as e:
            print(f"  > Error processing {image_path.name}: {e}")
            
    return known_face_encodings, known_face_names

def find_and_sort_faces_by_reference(events_dir, known_encodings, known_names):
    """
    Iterates through event photos, finds faces, and compares them against the
    known reference encodings. Matched photos are copied to a named folder.
    """
    print("--- Sorting event photos by reference ---")
    if not known_encodings:
        print("No reference faces loaded. Stopping sort process.")
        return

    for image_path in events_dir.rglob('*'):
        if not _is_image_file(image_path):
            continue
        
        print(f"Processing event photo: {image_path.name}")
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            # Use a set to track which people have been found in this image
            # to prevent copying the photo multiple times for the same person.
            people_found_in_image = set()

            for face_encoding in face_encodings:
                # Compare the found face with all known reference faces
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    
                    if name not in people_found_in_image:
                        # Create a directory for the person if it doesn't exist
                        person_dir = OUTPUT_DIR / name
                        person_dir.mkdir(exist_ok=True)
                        
                        # Copy the photo to that person's directory
                        shutil.copy2(image_path, person_dir)
                        print(f"  > Matched {name}. Copied photo to '{person_dir.name}' folder.")
                        people_found_in_image.add(name)
            
            if not people_found_in_image:
                 print("  > No known faces found in this photo.")

        except Exception as e:
            print(f"  > Error processing {image_path.name}: {e}")

def copy_reference_photos(ref_dir):
    """
    Copies the original reference photos into their corresponding output folders
    to make them easy to identify.
    """
    print("--- Copying reference photos to output folders ---")
    for image_path in ref_dir.rglob('*'):
        if not _is_image_file(image_path):
            continue
        
        name = image_path.stem
        person_dir = OUTPUT_DIR / name
        if person_dir.exists():
            shutil.copy2(image_path, person_dir)
            print(f"Copied reference for '{name}' to their folder.")

# --- Workflow 2: Automatic Discovery ---

def find_unique_faces(events_dir, tolerance=0.6):
    """
    Analyzes all event photos to discover unique individuals.
    It saves a cropped portrait of each unique person for later tagging.
    """
    print("--- Discovering unique faces in event photos ---")
    discovered_encodings = []
    all_face_metadata = [] # Stores info about every face found

    for image_path in events_dir.rglob('*'):
        if not _is_image_file(image_path):
            continue
            
        print(f"Discovering in: {image_path.name}")
        try:
            image_data = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image_data)
            face_encodings = face_recognition.face_encodings(image_data, face_locations)

            if not face_encodings:
                print("  > No faces found.")
                continue

            for i, face_encoding in enumerate(face_encodings):
                metadata = {'path': image_path, 'encoding': face_encoding}
                all_face_metadata.append(metadata)

                # Check if this face is a new, unique person
                if not discovered_encodings:
                    discovered_encodings.append(face_encoding)
                    _save_portrait(image_path, face_locations[i], len(discovered_encodings) - 1)
                else:
                    matches = face_recognition.compare_faces(discovered_encodings, face_encoding, tolerance)
                    if True not in matches:
                        discovered_encodings.append(face_encoding)
                        _save_portrait(image_path, face_locations[i], len(discovered_encodings) - 1)

        except Exception as e:
            print(f"  > Error processing {image_path.name}: {e}")
            
    print(f"--- Discovery complete. Found {len(discovered_encodings)} unique people. ---")
    return discovered_encodings, all_face_metadata

def _save_portrait(image_path, location, person_index):
    """Helper function to crop and save a face portrait."""
    top, right, bottom, left = location
    
    image = Image.open(image_path)
    face_image = image.crop((left, top, right, bottom))
    
    # Add some padding to the portrait
    padding = 20
    padded_image = Image.new(face_image.mode, (face_image.width + 2*padding, face_image.height + 2*padding), (255, 255, 255, 0))
    padded_image.paste(face_image, (padding, padding))

    portrait_path = UNKNOWN_PORTRAITS_DIR / f"person_{person_index}.png"
    padded_image.save(portrait_path)
    print(f"  > Saved new unique portrait: {portrait_path.name}")

def sort_photos_by_discovered_faces(all_face_metadata, discovered_encodings, user_names, tolerance=0.6):
    """
    Sorts photos based on the names provided by the user for the discovered faces.
    """
    print("--- Sorting photos based on user tags ---")
    # Create a mapping from person index to the name given by the user
    name_map = {idx: name for idx, name in user_names.items() if name}

    for metadata in all_face_metadata:
        face_encoding = metadata['encoding']
        image_path = metadata['path']

        matches = face_recognition.compare_faces(discovered_encodings, face_encoding, tolerance)
        
        if True in matches:
            match_index = matches.index(True)
            
            if match_index in name_map:
                name = name_map[match_index]
                
                person_dir = OUTPUT_DIR / name
                person_dir.mkdir(exist_ok=True)
                
                # Copy photo if it's not already there
                if not (person_dir / image_path.name).exists():
                    shutil.copy2(image_path, person_dir)
                    print(f"Sorted '{image_path.name}' into '{name}' folder.")

# --- Finalization ---

def create_download_zip(output_dir, download_path):
    """
    Creates a final zip file of the sorted output directory for easy downloading.
    """
    print(f"--- Creating final zip file at '{download_path}' ---")
    try:
        shutil.make_archive(str(download_path.with_suffix('')), 'zip', str(output_dir))
        print("Zip file created successfully.")
    except Exception as e:
        print(f"Error creating zip file: {e}")
