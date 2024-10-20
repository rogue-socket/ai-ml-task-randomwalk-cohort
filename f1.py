#%%
import pytesseract
import re
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#%%

img = Image.open('377975602-e5695bba-0dfa-4144-8c09-1cabf8096b3e.png')
#%%
# Normal OCR on the image
text = pytesseract.image_to_string(img)
print(text)
#%%
# Resize image to improve OCR results
# resized_img = img.resize((int(img.width * 1.5), int(img.height * 1.5)))
# resized_img.show()

# Convert the image to grayscale
# gray_img = resized_img.convert("L")
# gray_img.show()

# Convert image to black and white (thresholding)
# bw_img = gray_img.point(lambda x: 0 if x < 128 else 255, '1')
# bw_img.show()
#%% md
# # Getting data by converting each scanned data to boxes
# box_data = pytesseract.image_to_boxes(img)
# print(box_data)
#%%
# Getting all sorts of data that can be extracted from the image, converted to a dictionary
data=pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

# Pretty printing the data
for elem in data:
    print(f"{elem} : {data[elem]}, {len(data[elem])}")
#%% md
# Trying to print the words based on the "block_numbers" data point?
# Getting a set of all the block numbers
# ```block_numbers_set = set(data['block_num'])```
# All the data will be stored in block_dict with the key being the "block number"
# 
# ```
# block_dict = {}
# for unique_block_number in block_numbers_set:
#     for i, block_number in enumerate(data["block_num"]):
#         if block_number == unique_block_number:
#             # Exclude all the empty strings
#             temp_text = data['text'][i]
#             temp_text = temp_text.strip()
#             if temp_text:
#                 if block_number in block_dict:
#                     block_dict[block_number].append(temp_text)
#                 else:
#                     block_dict[block_number] = [temp_text]
#             else:
#                 continue
# ```
# 
# Pretty printing the data
# ```
# for elem in block_dict:
#     print(f"{elem} : {block_dict[elem]}")  
# ``` 
# 
#   
#%% md
# Copying the data to alternate dictionary for more analysis
#%%
data2 = data.copy()
print(data2)
#%%
# Filter out empty strings by creating a mask for non-empty text
non_empty_indices = [i for i, text in enumerate(data2['text']) if (text.strip() and re.sub(r'[^\w\s]|_', '', text))]

# Apply the mask to all categories in data2
for cat in data2:
    data2[cat] = [data2[cat][i] for i in non_empty_indices]

# Pretty printing the cleaned data
for elem in data2:
    print(f"{elem} : {data2[elem]}")
        
#%%
# Making a dictionary where all the key is the word and the value is the data extracted from the OCR of that word
data_word = {}
for i, word in enumerate(data2['text']):
    data_word[(i, word)] = {}
    for datapoint in data2:
        data_word[(i, word)][datapoint] = data2[datapoint][i]
        
for p in data_word:
    print(f"{p} : {data_word[p]}")
#%%
# Making a dictionary with the coordinates of each block, in the order left, top, width, height and the text it has 
coordinates = {}
for word in data_word:
    coordinates[word] = [data_word[word]['left'], data_word[word]['top'], data_word[word]['width'], data_word[word]['height'], data_word[word]['text']]
    
print(coordinates)
#%% md
# # GPT Generated Code -> to group boxes together
#%%
# # Helper function to check if two boxes are close with a threshold
# def are_boxes_close(box1, box2, threshold):
#     x1, y1, w1, h1, t1 = box1
#     x2, y2, w2, h2, t2 = box2
# 
#     # Check if boxes are within the threshold proximity
#     if x1 + w1 + threshold >= x2 and x2 + w2 + threshold >= x1 and \
#        y1 + h1 + threshold >= y2 and y2 + h2 + threshold >= y1:
#         return True
#     return False
# 
# # Function to group boxes
# def group_boxes(boxes, threshold):
#     n = len(boxes)
#     graph = defaultdict(list)
#     
#     # Build the adjacency list by checking which boxes are close to each other
#     for i in range(n):
#         for j in range(i+1, n):
#             if are_boxes_close(boxes[i], boxes[j], threshold):
#                 graph[i].append(j)
#                 graph[j].append(i)
# 
#     # Function to perform DFS and find connected components
#     def dfs(node, visited, group):
#         visited[node] = True
#         group.append(node)
#         for neighbor in graph[node]:
#             if not visited[neighbor]:
#                 dfs(neighbor, visited, group)
# 
#     visited = [False] * n
#     groups = []
# 
#     # Find all groups using DFS
#     for i in range(n):
#         if not visited[i]:
#             group = []
#             dfs(i, visited, group)
#             groups.append(group)
#     
#     # Return the grouped box indices (or could return the boxes themselves)
#     return [[boxes[i] for i in group] for group in groups]
# 
# # Example usage:
# # boxes = [(0, 0, 2, 2, 'yash'), (5, 5, 2, 2, 'joseph'), (1, 1, 2, 2, 'ani'), (10, 10, 2, 2, 'dhruv')]
# # groups = group_boxes(boxes, threshold=2)
# # print(groups)
#%%
# Formatting the data we have to fit the input style of the function created
input_coordinates_text = []
for elem in coordinates:
    input_coordinates_text.append(tuple(coordinates[elem]))
print(input_coordinates_text)

# Passing the inputs into the function
# groups = group_boxes(input_coordinates_text, threshold=20)

# for elem in groups:
#     print(elem)
#%%
# Forming the blocks of text and
# sorting the groups based on the order they appear from the top left to bottom right
from collections import defaultdict

# Helper function to check if two boxes are close
def are_boxes_close(box1, box2, threshold):
    x1, y1, w1, h1, t1 = box1
    x2, y2, w2, h2, t2 = box2

    # Check if boxes are within the threshold proximity
    if x1 + w1 + threshold >= x2 and x2 + w2 + threshold >= x1 and \
       y1 + h1 + threshold >= y2 and y2 + h2 + threshold >= y1:
        return True
    return False

# Function to group boxes
def group_boxes(boxes, threshold):
    n = len(boxes)
    graph = defaultdict(list)
    
    # Build the adjacency list by checking which boxes are close to each other
    for i in range(n):
        for j in range(i+1, n):
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

groups = group_boxes(input_coordinates_text, threshold=20)

# Print the sorted groups
for i, group in enumerate(groups):
    print(f"Group {i+1}: {group}")

#%%
# Attempting to get the order right
for group in groups:
    group.sort(key=lambda box: (box[1], box[0]))  # Sort by (x, y)

# Sort the groups themselves by the top-left coordinate of the first box in each group
groups.sort(key=lambda group: (group[0][0], group[0][1]))

# Print the sorted groups
for i, group in enumerate(groups):
    print(f"Group {i+1}: {group}")
#%% md
# # Code to mark heading and the subtext
#%%
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

# Create subgroups
subgroups = create_subgroups(groups, 5)

print(subgroups)

# Print the subgroups for each block group
for i, group in enumerate(subgroups):
    print(f"Group {i+1}:")
    print(f"  Heading: {group['heading']}")
    print(f"  Subtext: {group['subtext']}")

#%%
def sort_within_blocks(subgroups, margin_of_error=2):
    def sort_boxes(boxes):
        # Sort based on y-coordinate with a margin of error, and within the same y, sort by x-coordinate
        sorted_boxes = sorted(boxes, key=lambda box: (round(box[1] / margin_of_error), box[0]))  # box[1] is y, box[0] is x
        return sorted_boxes

    for group in subgroups:
        group['heading'] = sort_boxes(group['heading'])
        group['subtext'] = sort_boxes(group['subtext'])
    
    return subgroups

# Sort within blocks using the margin of error
sorted_subgroups = sort_within_blocks(subgroups, margin_of_error=6)

# Print the sorted blocks
for i, group in enumerate(sorted_subgroups):
    print(f"Group {i+1}:")
    print(f"  Heading: {group['heading']}")
    print(f"  Subtext: {group['subtext']}")

#%%
for elem in sorted_subgroups:
    print(elem)
#%%
answer_dict = {}
for elem in sorted_subgroups:
    heading_text = " ".join([heading[-1] for heading in elem['heading']])
    subtext_text = " ".join([subtext[-1] for subtext in elem['subtext']])
    answer_dict[heading_text] = subtext_text

for elem in answer_dict:
    print(f"{elem} : {answer_dict[elem]}")