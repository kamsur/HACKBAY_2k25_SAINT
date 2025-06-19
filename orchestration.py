# Orchestration script to connect ProductManager, SoftwareDeveloper, SoftwareTester, and ComplianceManager

from agents.ProductManager import agent as product_manager_agent
from agents.SoftwareDeveloper import agent as software_developer_agent, extract_python_code
from agents.SoftwareTester import agent as software_tester_agent, extract_python_code as extract_test_code
import agents.ComplianceManager as compliance_manager
import os
import subprocess
import time
from codecarbon import EmissionsTracker

# Step 1: Product Manager receives the initial product prompt
product_prompt = (
    "Create a webapp for a secure system where employees will upload payslips, tax documents, and transaction receipts."
)

print("\n--- Product Manager (Backlog Generation) ---\n")
product_manager_response = product_manager_agent.run(product_prompt)
print(product_manager_response.content)

# Step 2: Software Developer receives the backlog and generates code
print("\n--- Software Developer (Code Generation) ---\n")
developer_response = software_developer_agent.run(product_manager_response.content)
print(developer_response.content)

# Extract code blocks and save them as files
code_blocks = extract_python_code(developer_response.content)
generated_code_files = []
for i, code in enumerate(code_blocks, 1):
    filename = f"generated_code_{i}.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code.strip())
    generated_code_files.append(filename)

# Step 3: Software Tester receives the code and generates tests
print("\n--- Software Tester (Test Generation) ---\n")
test_files = []
for code_file in generated_code_files:
    with open(code_file, 'r', encoding='utf-8') as f:
        code_content = f.read()
    test_prompt = f"Generate comprehensive tests for the following code. Output only the test code as a Python code block.\n\n{code_content}"
    tester_response = software_tester_agent.run(test_prompt)
    print(tester_response.content)
    test_blocks = extract_test_code(tester_response.content)
    for j, test_code in enumerate(test_blocks, 1):
        test_filename = f"test_{os.path.splitext(code_file)[0]}_{j}.py"
        with open(test_filename, "w", encoding="utf-8") as tf:
            tf.write(test_code.strip())
        test_files.append(test_filename)

# Step 3.5: Measure runtime and energy consumption of all generated code files
print("\n--- Runtime & Energy Consumption (CodeCarbon) ---\n")
for code_file in generated_code_files:
    print(f"\nRunning {code_file} with CodeCarbon tracker...")
    tracker = EmissionsTracker(project_name=code_file, output_dir=".", output_file=f"{code_file}_emissions.csv")
    tracker.start()
    start_time = time.time()
    try:
        result = subprocess.run(["python", code_file], capture_output=True, text=True, timeout=120)
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"{code_file} timed out.")
    end_time = time.time()
    emissions: float = tracker.stop()
    runtime = end_time - start_time
    print(f"Runtime for {code_file}: {runtime:.2f} seconds")
    print(f"Estimated CO2 emissions for {code_file}: {emissions:.6f} kgCO2eq")
    # Append report to AppData\\carbon.txt
    appdata_path = os.path.expandvars(r'%APPDATA%')
    carbon_report_path = os.path.join(appdata_path, 'carbon.txt')
    with open(carbon_report_path, 'a', encoding='utf-8') as report_file:
        report_file.write(f"{code_file}: Runtime = {runtime:.2f} seconds, CO2 Emissions = {emissions:.6f} kgCO2eq\n")

# Step 4: Compliance Manager checks all code and test files for compliance
print("\n--- Compliance Manager (Compliance Check) ---\n")
all_files = generated_code_files + test_files
for file in all_files:
    with open(file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    compliance_prompt = f"Check if the following code complies with all relevant regulations and policies.\n\n{file_content}"
    compliance_response = compliance_manager.query_llm(compliance_prompt)
    print(f"\nCompliance check for {file}:\n{compliance_response}\n")
