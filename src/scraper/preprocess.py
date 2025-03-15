import pathlib
import tqdm
import pymupdf
import pymupdf4llm



def convert_to_markdown_and_save(file, save_at):
    md_text = pymupdf4llm.to_markdown(file)
    save_at.write_bytes(md_text.encode())


def convert_to_text_and_save(file, save_at):
    doc = pymupdf.open(file)
    text = ""

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()

    save_at.write_bytes(text.encode())


def process_pdf(file):
    file_name = file.stem
    new_md_file = md_data_dir / f"{file_name}.md"
    new_txt_file = txt_data_dir / f"{file_name}.txt"

    convert_to_markdown_and_save(file, new_md_file)
    convert_to_text_and_save(file, new_txt_file)


data_dir = pathlib.Path("./Data")

# Directories for raw, txt, and markdown filesś
raw_data_dir = data_dir / "raw"
txt_data_dir = data_dir / "txt"
md_data_dir = data_dir / "markdown"

txt_data_dir.mkdir(parents=True, exist_ok=True)
md_data_dir.mkdir(parents=True, exist_ok=True)

raw_files = [x for x in raw_data_dir.iterdir()]

for file in tqdm.tqdm(raw_files):
    if file.suffix.lower() == ".pdf":
        process_pdf(file)

