import os
import zipfile

function_name = "lambda_function"


def create_zip_package(output_filename="deployment_package.zip"):
    import site

    site_packages_path = None
    for path in site.getsitepackages():
        if "venv" in path and "site-packages" in path:
            site_packages_path = path
            break

    if not site_packages_path:
        print("Error: Could not find site-packages in the virtual environment.")
        print(
            "Please ensure your virtual environment is activated or adjust the path manually."
        )
        return

    print(f"Found site-packages at: {site_packages_path}")

    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(site_packages_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, site_packages_path)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

        lambda_function_file = f"{function_name}.py"
        if os.path.exists(lambda_function_file):
            zipf.write(lambda_function_file, os.path.basename(lambda_function_file))
            print(f"Added: {os.path.basename(lambda_function_file)}")
        else:
            print(f"Warning: {lambda_function_file} not found in current directory.")

    print(f"\nDeployment package '{output_filename}' created successfully!")


if __name__ == "__main__":
    create_zip_package()
