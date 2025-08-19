import os
import zipfile
from pathlib import Path
import face_recognition
import shutil

# --- Constants for our project directories ---
# We'll store extracted files in a temporary directory.
TEMP_DIR = Path("temp_files")
EXTRACTED_EVENTS_DIR = TEMP_DIR / "event_photos"
EXTRACTED_REFERENCES_DIR = TEMP_DIR / "reference_photos"
OUTPUT_DIR = Path("sorted_photos")

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

    # Create the main temporary and output directories
    TEMP_DIR.mkdir(exist_ok=True)
    EXTRACTED_EVENTS_DIR.mkdir(exist_ok=True, parents=True)
    EXTRACTED_REFERENCES_DIR.mkdir(exist_ok=True, parents=True)
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
            # Load the image
            image = face_recognition.load_image_file(image_path)
            # Get face encodings. We assume one face per reference image.
            encodings = face_recognition.face_encodings(image)

            if encodings:
                # Get the person's name from the filename
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

def find_and_sort_faces(events_dir, known_encodings, known_names):
    """
    Goes through event photos, finds faces, and copies them to sorted folders.
    """
    print(f"\nStarting to process event photos in '{events_dir}'...")
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    
    # Create a folder for photos where no known faces are found
    unknown_dir = OUTPUT_DIR / "_unknown"
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

            found_known_person = False
            for face_encoding in face_encodings:
                # Compare this face with all known faces
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    print(f"  -> Found {name}!")

                    # Create a directory for this person if it doesn't exist
                    person_dir = OUTPUT_DIR / name
                    person_dir.mkdir(exist_ok=True)

                    # Copy the photo to that person's directory
                    shutil.copy(image_path, person_dir)
                    found_known_person = True
                    # We break after the first match to avoid copying the photo multiple times
                    # if multiple known people are in it. A more advanced version could handle this differently.
                    break 
            
            if not found_known_person:
                print("  -> Found faces, but none matched the references.")
                shutil.copy(image_path, unknown_dir)

        except Exception as e:
            print(f"  -> Error processing {image_path.name}: {e}")

    print("\n--- Photo sorting complete! ---")
    print(f"Sorted photos can be found in the '{OUTPUT_DIR}' directory.")


# --- Main execution block for testing ---
if __name__ == "__main__":
    print("--- Running a full test of the core logic ---")
    
    # 1. Clean and set up directories
    setup_directories()

    # 2. Simulate extracting zips (by creating dummy files)
    # In a real run, these files would come from the user's zip files.
    print("\n--- Simulating file extraction ---")
    # Create dummy reference images
    try:
        from PIL import Image
        Image.new('RGB', (100, 100), color = 'red').save(EXTRACTED_REFERENCES_DIR / 'Alice.png')
        Image.new('RGB', (100, 100), color = 'blue').save(EXTRACTED_REFERENCES_DIR / 'Bob.png')
        # Create dummy event images
        Image.new('RGB', (200, 200), color = 'green').save(EXTRACTED_EVENTS_DIR / 'event1.png')
        Image.new('RGB', (200, 200), color = 'yellow').save(EXTRACTED_EVENTS_DIR / 'event2.png')
        print("Dummy files created for testing.")
        # NOTE: For a real test, you'd replace these dummy files with actual photos of faces.
        # The face_recognition library will not find faces in these solid color images.
        # This test primarily checks the file operations and logic flow.
    except ImportError:
        print("Pillow is not installed. Cannot create dummy images for a full test.")
        print("Skipping face processing test.")

    # 3. Load reference faces
    known_encodings, known_names = load_reference_encodings(EXTRACTED_REFERENCES_DIR)

    # 4. Process event photos
    if known_encodings:
        find_and_sort_faces(EXTRACTED_EVENTS_DIR, known_encodings, known_names)
    else:
        print("\nSkipping photo sorting because no reference faces were loaded.")

    print("\n--- Core logic script test finished. ---")
