import os
import zipfile
from pathlib import Path
import face_recognition
import shutil
from collections import defaultdict

# --- Constants for our project directories ---
TEMP_DIR = Path("temp_files")
EXTRACTED_EVENTS_DIR = TEMP_DIR / "event_photos"
EXTRACTED_REFERENCES_DIR = TEMP_DIR / "reference_photos"
UNKNOWN_PORTRAITS_DIR = TEMP_DIR / "unknown_portraits"
OUTPUT_DIR = Path("sorted_photos")
DOWNLOAD_ZIP_PATH = Path("FaceFolio_Sorted.zip")

def setup_directories():
    """
    Creates the necessary temporary and output directories for the application.
    This ensures a clean state every time the program runs.
    """
    print("Setting up initial directories...")
    # Clean up old files before starting
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    if DOWNLOAD_ZIP_PATH.exists():
        os.remove(DOWNLOAD_ZIP_PATH)


    # Create the main temporary and output directories
    TEMP_DIR.mkdir(exist_ok=True)
    EXTRACTED_EVENTS_DIR.mkdir(exist_ok=True, parents=True)
    EXTRACTED_REFERENCES_DIR.mkdir(exist_ok=True, parents=True)
    UNKNOWN_PORTRAITS_DIR.mkdir(exist_ok=True, parents=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("Directories are ready.")


def extract_zip(zip_path, destination_path):
    """
    Extracts a zip file to a specified destination folder.
    """
    try:
        os.makedirs(destination_path, exist_ok=True)
        print(f"Extracting '{zip_path}' to '{destination_path}'...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)
        print("Extraction complete.")
        return True
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        print(f"Error during extraction: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")
        return False

# --- WORKFLOW 1 FUNCTIONS ---

def load_reference_encodings(references_dir):
    """
    Loads reference images and creates face encodings for each person.
    The image filename (without extension) is used as the person's name.
    """
    known_face_encodings = []
    known_face_names = []
    print(f"Loading reference images from '{references_dir}'...")

    for image_path in Path(references_dir).glob("*.*"):
        try:
            print(f"Processing reference: {image_path.name}")
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                person_name = image_path.stem
                known_face_encodings.append(encodings[0])
                known_face_names.append(person_name)
                print(f"  -> Learned encoding for: {person_name}")
            else:
                print(f"  -> Warning: No face found in {image_path.name}")
        except Exception as e:
            print(f"  -> Error processing {image_path.name}: {e}")
            
    print("Finished loading reference encodings.")
    return known_face_encodings, known_face_names

def find_and_sort_faces_by_reference(events_dir, known_encodings, known_names):
    """
    Goes through event photos, finds faces, and copies them to sorted folders based on references.
    """
    print(f"\nStarting to process event photos in '{events_dir}'...")
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    
    unknown_dir = OUTPUT_DIR / "_unknown_no_match"
    unknown_dir.mkdir(exist_ok=True)

    for image_path in Path(events_dir).rglob("*.*"):
        if image_path.suffix.lower() not in image_extensions:
            continue

        print(f"Scanning: {image_path.name}")
        try:
            event_image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(event_image)
            face_encodings = face_recognition.face_encodings(event_image, face_locations)

            if not face_encodings:
                print("  -> No faces found in this image.")
                shutil.copy(image_path, unknown_dir)
                continue

            unique_people_in_photo = set()

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    unique_people_in_photo.add(name)
            
            if unique_people_in_photo:
                for name in unique_people_in_photo:
                    print(f"  -> Found {name}!")
                    person_dir = OUTPUT_DIR / name
                    person_dir.mkdir(exist_ok=True)
                    shutil.copy(image_path, person_dir)
            else:
                print("  -> Found faces, but none matched the references.")
                shutil.copy(image_path, unknown_dir)

        except Exception as e:
            print(f"  -> Error processing {image_path.name}: {e}")

    print("\n--- Photo sorting by reference complete! ---")

# --- WORKFLOW 2 FUNCTIONS ---

def find_unique_faces(events_dir):
    """
    Finds all unique faces across all event photos without any prior references.
    Returns a list of encodings for each unique person.
    """
    print(f"\nStarting to find all unique faces in '{events_dir}'...")
    all_known_encodings = []
    all_face_metadata = [] # Store info about every face found
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    for image_path in Path(events_dir).rglob("*.*"):
        if image_path.suffix.lower() not in image_extensions:
            continue
        
        print(f"Scanning for unique faces in: {image_path.name}")
        try:
            image = face_recognition.load_image_file(image_path)
            locations = face_recognition.face_locations(image)
            encodings = face_recognition.face_encodings(image, locations)

            for i, encoding in enumerate(encodings):
                matches = face_recognition.compare_faces(all_known_encodings, encoding)

                if True not in matches:
                    print(f"  -> Found a new unique person (Person #{len(all_known_encodings) + 1})")
                    all_known_encodings.append(encoding)
                    
                    top, right, bottom, left = locations[i]
                    face_image = image[top:bottom, left:right]
                    portrait_path = UNKNOWN_PORTRAITS_DIR / f"person_{len(all_known_encodings)}.png"
                    
                    from PIL import Image
                    pil_image = Image.fromarray(face_image)
                    pil_image.save(portrait_path)
                    
                all_face_metadata.append({'path': image_path, 'encoding': encoding})

        except Exception as e:
            print(f"  -> Error processing {image_path.name}: {e}")
            
    print(f"\nFound {len(all_known_encodings)} unique people.")
    return all_known_encodings, all_face_metadata


def sort_photos_by_discovered_faces(all_face_metadata, discovered_encodings, user_names):
    """
    Sorts photos into folders based on the newly discovered faces and user-provided names.
    """
    print("\nSorting all photos based on discovered faces and new names...")
    person_to_photos = defaultdict(set)

    for metadata in all_face_metadata:
        matches = face_recognition.compare_faces(discovered_encodings, metadata['encoding'])
        if True in matches:
            match_index = matches.index(True)
            person_name = user_names.get(match_index, f"person_{match_index + 1}")
            person_to_photos[person_name].add(metadata['path'])

    for person_name, photo_paths in person_to_photos.items():
        person_dir = OUTPUT_DIR / person_name
        person_dir.mkdir(exist_ok=True)
        print(f"Copying {len(photo_paths)} photos for {person_name}...")
        for path in photo_paths:
            shutil.copy(path, person_dir)
            
    print("\n--- Photo sorting by discovered faces complete! ---")

# --- FINAL OUTPUT FUNCTIONS ---

def copy_reference_photos(references_dir):
    """
    Copies the original reference photos into their corresponding sorted folders.
    """
    print("\nAdding reference photos to sorted folders...")
    for ref_path in Path(references_dir).glob("*.*"):
        person_name = ref_path.stem
        person_dir = OUTPUT_DIR / person_name
        if person_dir.exists():
            # Name the reference photo to appear first (e.g., "000_Alice.jpg")
            new_ref_name = f"000_{ref_path.name}"
            shutil.copy(ref_path, person_dir / new_ref_name)
            print(f"  -> Copied reference for {person_name}")

def create_download_zip(source_dir, output_path):
    """
    Creates a zip file from a source directory.
    """
    print(f"\nCreating final zip file at '{output_path}'...")
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, archive_name)
        print("Successfully created download zip.")
        return True
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return False

# --- Main execution block for testing ---
if __name__ == "__main__":
    setup_directories()
    
    # --- To test WORKFLOW 1 (with references) ---
    print("\n--- TESTING WORKFLOW 1: With Reference Photos ---")
    # Simulate extraction by creating dummy files with faces
    # IMPORTANT: For this test to work, you MUST have actual image files with faces.
    # Replace "path/to/your/alice.jpg" with real file paths on your computer.
    try:
        # shutil.copy("path/to/your/alice.jpg", EXTRACTED_REFERENCES_DIR / "Alice.jpg")
        # shutil.copy("path/to/your/bob.jpg", EXTRACTED_REFERENCES_DIR / "Bob.jpg")
        # shutil.copy("path/to/your/event_photo_with_alice.jpg", EXTRACTED_EVENTS_DIR)
        print("NOTE: Dummy file creation is commented out. Add your own images to test.")
    except FileNotFoundError:
        print("Could not find test images. Please update the paths in core.py")

    known_encodings, known_names = load_reference_encodings(EXTRACTED_REFERENCES_DIR)
    if known_encodings:
        find_and_sort_faces_by_reference(EXTRACTED_EVENTS_DIR, known_encodings, known_names)
        copy_reference_photos(EXTRACTED_REFERENCES_DIR)
        create_download_zip(OUTPUT_DIR, DOWNLOAD_ZIP_PATH)
    else:
        print("Skipping Workflow 1 test: No reference photos found in temp_files/reference_photos.")

    print("\n--- Core logic script test finished. ---")
