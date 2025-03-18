import os
import random
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split


def reduce_and_split_dataset(image_dir, label_dir, output_dir, reduction_percentage=20, valid_ratio=0.2):

    train_img_dir = Path(output_dir) / "train" / "images"
    train_lbl_dir = Path(output_dir) / "train" / "labels"
    valid_img_dir = Path(output_dir) / "valid" / "images"
    valid_lbl_dir = Path(output_dir) / "valid" / "labels"

    for d in [train_img_dir, train_lbl_dir, valid_img_dir, valid_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)

    image_files = sorted(Path(image_dir).glob("*.jpg"))
    label_files = sorted(Path(label_dir).glob("*.txt"))

    paired_files = [(img, lbl) for img in image_files
                    if (lbl := Path(label_dir) / (img.stem + ".txt")).exists()]

    print(f"Total pairs before reduction: {len(paired_files)}")

    num_to_remove = int(len(paired_files) * (reduction_percentage / 100))
    to_remove = random.sample(paired_files, num_to_remove)

    for img, lbl in to_remove:
        img.unlink()
        lbl.unlink()

    remaining_pairs = [(img, lbl) for img in Path(image_dir).glob("*.jpg")
                       if (lbl := Path(label_dir) / (img.stem + ".txt")).exists()]

    print(f"Total pairs after reduction: {len(remaining_pairs)}")

    # Split into training and validation sets
    train_pairs, valid_pairs = train_test_split(remaining_pairs, test_size=valid_ratio, random_state=42)

    # Copy files to new structure
    def copy_pairs(pairs, img_dest, lbl_dest):
        for img, lbl in pairs:
            shutil.copy(img, img_dest / img.name)
            shutil.copy(lbl, lbl_dest / lbl.name)

    copy_pairs(train_pairs, train_img_dir, train_lbl_dir)
    copy_pairs(valid_pairs, valid_img_dir, valid_lbl_dir)

    print(f"Dataset split completed:")
    print(f"- Training pairs: {len(train_pairs)}")
    print(f"- Validation pairs: {len(valid_pairs)}")


image_dir = 'bdd100/images-mini'
label_dir = 'bdd100/labels-mini-txt'
output_dir = 'bdd100/split_data'


reduction_percentage = 0  # Adjust the percentage of data to remove
valid_ratio = 0.2  # 20% of the remaining data goes to validation

# Run the script
reduce_and_split_dataset(image_dir, label_dir, output_dir, reduction_percentage, valid_ratio)