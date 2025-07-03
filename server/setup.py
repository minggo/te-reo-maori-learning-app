from setuptools import setup, find_packages

def parse_requirements(fname):
    reqs = []
    with open(fname, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines, comment lines, and recursive includes
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            reqs.append(line)
    return reqs

# Parse runtime dependencies from requirements.txt
install_reqs = parse_requirements("requirements.txt")
# Parse development-only dependencies from dev-requirements.txt
dev_reqs = parse_requirements("dev-requirements.txt")

setup(
    name="maori_learning_app",
    version="0.1.0",
    packages=find_packages(),  # Automatically discover packages under app/
    include_package_data=True,  # Include package data specified in MANIFEST.in
    install_requires=install_reqs,  # Runtime dependencies
    extras_require={
        "dev": dev_reqs,  # Development and testing dependencies
    },
    # Additional metadata (author, license, entry_points, etc.) can go here
)
