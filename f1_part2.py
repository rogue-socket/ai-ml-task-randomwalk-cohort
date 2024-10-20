import pytesseract
import re
from PIL import Image
from collections import defaultdict
def are_boxes_close(box1, box2, threshold):
    x1, y1, w1, h1, t1 = box1
    x2, y2, w2, h2, t2 = box2

    # Check if boxes are within the threshold proximity
    if x1 + w1 + threshold >= x2 and x2 + w2 + threshold >= x1 and \
       y1 + h1 + threshold >= y2 and y2 + h2 + threshold >= y1:
        return True
    return False
def group_boxes(boxes, threshold):
    n = len(boxes)
    graph = defaultdict(list)

    # Build the adjacency list by checking which boxes are close to each other
    for i in range(n):
        for j in range(i + 1, n):
            if are_boxes_close(boxes[i], boxes[j], threshold):
                graph[i].append(j)
                graph[j].append(i)

    # Function to perform DFS and find connected components
    def dfs(node, visited, group):
        visited[node] = True
        group.append(node)
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor, visited, group)

    visited = [False] * n
    groups = []

    # Find all groups using DFS
    for i in range(n):
        if not visited[i]:
            group = []
            dfs(i, visited, group)
            groups.append(group)

    # Extract the boxes based on their group indices
    grouped_boxes = [[boxes[i] for i in group] for group in groups]

    # Sort each group by top-left coordinate (x, y) and sort groups accordingly
    for group in grouped_boxes:
        group.sort(key=lambda box: (box[0], box[1]))  # Sort by (x, y)

    # Sort the groups themselves by the top-left coordinate of the first box in each group
    grouped_boxes.sort(key=lambda group: (group[0][0], group[0][1]))

    return grouped_boxes
def create_subgroups(grouped_boxes, heading_threshold):
    subgroups = []

    for group in grouped_boxes:
        # Sort the group by y-coordinate to ensure top-to-bottom order
        group.sort(key=lambda box: (box[1], box[0]))  # Sort by y-coordinate, then by x-coordinate for left-to-right order

        # Initialize heading and subtext lists
        heading = []
        subtext = []

        # Assume the first block is part of the heading
        current_y = group[0][1]
        # print(f"current_y : {current_y}")
        for box in group:
            x, y, w, h, text = box
            # If the current block's y-coordinate is close enough to the current_y (within a threshold), it's part of the heading
            if abs(y - current_y) <= heading_threshold:
                heading.append(box)  # Add block to heading
            else:
                subtext.append(box)  # Add remaining blocks to subtext
            # current_y = y  # Update current_y for the next iteration

        # Append the heading and subtext as subgroups for this group
        subgroups.append({
            'heading': heading,
            'subtext': subtext
        })

    return subgroups
def sort_within_blocks(subgroups, margin_of_error=2):
    def sort_boxes(boxes):
        # Sort based on y-coordinate with a margin of error, and within the same y, sort by x-coordinate
        sorted_boxes = sorted(boxes,
                              key=lambda box: (round(box[1] / margin_of_error), box[0]))  # box[1] is y, box[0] is x
        return sorted_boxes

    for group in subgroups:
        group['heading'] = sort_boxes(group['heading'])
        group['subtext'] = sort_boxes(group['subtext'])

    return subgroups

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
img = Image.open('sample.jpeg')
img = img.convert("L")
img = img.point(lambda p: 255 if p > 200 else 0)
img.show()
answer_dict = {}

# Normal OCR on the image
text = pytesseract.image_to_string(img)

# Getting data by converting each scanned data to boxes
box_data = pytesseract.image_to_boxes(img)

# Getting all sorts of data that can be extracted from the image, converted to a dictionary
data=pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

data2 = data.copy()

# Getting rid of all the useless data like empty strings
# Filter out empty strings by creating a mask for non-empty text
non_empty_indices = [i for i, text in enumerate(data2['text']) if (text.strip() and re.sub(r'[^\w\s]|_', '', text))]

# Apply the mask to all categories in data2
for cat in data2:
    data2[cat] = [data2[cat][i] for i in non_empty_indices]

# Making a dictionary where all the key is the word and the value is the data extracted from the OCR of that word
data_word = {}
for i, word in enumerate(data2['text']):
    data_word[(i, word)] = {}
    for datapoint in data2:
        data_word[(i, word)][datapoint] = data2[datapoint][i]

# Making a dictionary with the coordinates of each block, in the order left, top, width, height and the text it has 
coordinates = {}
for word in data_word:
    coordinates[word] = [data_word[word]['left'], data_word[word]['top'], data_word[word]['width'], data_word[word]['height'], data_word[word]['text']]


# Formatting the data we have to fit the input style of the function created
input_coordinates_text = []
for elem in coordinates:
    input_coordinates_text.append(tuple(coordinates[elem]))

thresh = 1
groups = []
while(len(groups) != 14):
    thresh += 1
    groups = group_boxes(input_coordinates_text, thresh)

# getting the order right
for group in groups:
    group.sort(key=lambda box: (box[1], box[0]))  # Sort by (y, x)

# Sort the groups themselves by the top-left coordinate of the first box in each group
groups.sort(key=lambda group: (group[0][0], group[0][1]))

# Create subgroups
subgroups = create_subgroups(groups, 5)

# Sort within blocks using the margin of error
sorted_subgroups = sort_within_blocks(subgroups, margin_of_error=6)

for elem in sorted_subgroups:
    heading_text = " ".join([re.sub(r'[^\w\s]|_', '', heading[-1]) for heading in elem['heading']])
    subtext_text = " ".join([re.sub(r'[^\w\s]|_', '', subtext[-1]) for subtext in elem['subtext']])
    answer_dict[heading_text] = subtext_text

for elem in answer_dict:
    print(f"{elem} : {answer_dict[elem]}")