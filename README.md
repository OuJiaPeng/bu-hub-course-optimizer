# BU HUB Course Optimizer

Give it a list of HUB requirements you need, gives you all the combination of classes that can satisfy it.

This tool uses integer linear programming (ILP) to find the minimum number of BU courses that satisfy a student’s personalized Hub requirements.

---

## Features

- Customizable HUB requirement input
- Course filtering by department, title, or course code
- Automatically selects the smallest course combination
- Generates multiple valid optimal combinations

---

## How to use

```bash
git clone https://github.com/OuJiaPeng/bu-hub-course-optimizer.git
cd bu-hub-course-optimizer

# Install the required packages:

pip install -r requirements.txt

# Edit the ILP for HUB (Jupyter Notebook), change filters as you please
# Run the ILP for HUB:

jupyter notebook "notebooks/ILP for HUB.ipynb"
```

