import json
import re
import argparse

def update_md_links(json_path, md_path):
    # Load the JSON file that contains the mappings.
    # Expected JSON structure:
    # [
    #     {
    #         "mapping": {
    #             "<some_key>": {
    #                 "children": [...],
    #                 "message": {
    #                     "metadata": {
    #                         "content_references": [
    #                             {
    #                                 "matched_text": "【32†L1-L8】",
    #                                 "url": "http://example.com/link1",
    #                                 "title": "Link Title 1"
    #                             },
    #                             ...
    #                         ]
    #                     }
    #                 }
    #             },
    #             ... additional mappings ...
    #         }
    #     },
    #     ... possibly more entries ...
    # ]
    with open(json_path, "r", encoding="utf-8") as jf:
        links_data = json.load(jf)
    
    # Read the Markdown file content.
    with open(md_path, "r", encoding="utf-8") as mf:
        md_content = mf.read()
    
    # Prepare containers for footnotes.
    footnote_map = {}      # Maps a matched_text to its footnote number.
    footnotes = {}         # Maps footnote number to its definition (title - url).
    footnote_counter = 1
    
    # Iterate through each mapping in the JSON structure and build footnotes.
    for k, v in links_data[0]['mapping'].items():
        # Process only if there are no children for this mapping.
        if len(v.get('children', [])) == 0:
            for ref in v['message']['metadata']['content_references']:
                matched_text = ref['matched_text']
                if matched_text not in footnote_map:
                    footnote_map[matched_text] = footnote_counter
                    footnotes[footnote_counter] = f"[{ref['title']}]({ref['url']})"
                    footnote_counter += 1
                marker = f"[^{footnote_map[matched_text]}]"
                # Replace every occurrence of the matched_text with the footnote marker.
                md_content = re.sub(re.escape(matched_text), marker, md_content)
    
    # Append footnotes at the end of the markdown content.
    md_content = md_content.strip() + "\n\n"
    for i in sorted(footnotes.keys()):
        md_content += f"[^{i}]: {footnotes[i]}\n"

    # Construct the filename for the updated Markdown file.
    updated_md_path = md_path.rsplit('.', 1)[0] + "_updated.md"
    # Write the updated content to the new Markdown file.
    with open(updated_md_path, "w", encoding="utf-8") as mf:
        mf.write(md_content)
    
    print(f"Updated Markdown file saved as: {updated_md_path}")
    
    return md_content

def main():
    parser = argparse.ArgumentParser(description="Update markdown links with footnotes")
    parser.add_argument("--json", required=True, help="Path to the JSON file with link mappings")
    parser.add_argument("--md", required=True, help="Path to the Markdown file to update")
    args = parser.parse_args()

    updated = update_md_links(args.json, args.md)
    print("Successfully updated the markdown file.")

if __name__ == "__main__":
    main() 