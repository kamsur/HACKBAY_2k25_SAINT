import re
from typing import List, Tuple

def extract_all_sections(markdown: str) -> List[str]:
    """
    Extracts all sections starting with '## n.' into a list.
    """
    pattern = r"(## \d+\..*?)(?=\n## \d+\.|\Z)"
    return [match.strip() for match in re.findall(pattern, markdown, re.DOTALL)]

def extract_definition_of_done(section_text: str) -> List[str]:
    """
    Extracts the 'Definition of Done' items from a section.
    """
    pattern = r"\*\*Definition of Done\*\*:(.*?)(?=\n\S|\Z)"
    match = re.search(pattern, section_text, re.DOTALL)
    if match:
        lines = match.group(1).strip().splitlines()
        return [line.strip() for line in lines if line.strip()]
    return []

def extract_sections_and_done_items(markdown: str) -> Tuple[List[str], List[List[str]]]:
    """
    Returns a list of full sections and a list of their corresponding 'Definition of Done' items.
    """
    sections = extract_all_sections(markdown)
    done_items = [extract_definition_of_done(section) for section in sections]
    return sections, done_items

# --------------------
# Example usage:
# --------------------
if __name__ == "__main__":
    with open(r"C:\Users\arkaniva\Downloads\HackBay\HACKBAY_2k25_SAINT\AppData\KanbanBoardData.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()

    sections_list, done_items_list = extract_sections_and_done_items(markdown_content)

    print("=== Sections ===")
    pattern = r'\*\*Title\*\*:\s*(.*?)\n(.*)'

    for i, section in enumerate(sections_list, 1):
        print(f"\n{section}")
        

        match = re.search(pattern, section, re.DOTALL)
        if match:
            title = match.group(1).strip()
            rest_of_text = match.group(2).strip()
            print("Title:", title)
            print("\nRemaining Text:\n", rest_of_text)
        break

    # print("\n=== Definition of Done Items ===")
    # for i, done_items in enumerate(done_items_list, 1):
    #     print(f"\n--- Section {i} DoD ---")
    #     for item in done_items:
    #         print("-", item)
