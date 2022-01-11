import os
import subprocess
import argparse

path_render_script = "blender_main.py"

TESTS = {"test_cameras": ("test_cameras.py", "test_cameras.blend")}

def run(name, path_to_blender, path_to_py_test, path_to_blend_file):
    print('Running test: %s' % name)
    print('=====================================')

    python_script_full_path = os.path.join(dirname, python_script)
    blend_file_full_path = os.path.join(dirname, blend_file)
    cmd = "{} --background {} --python {}".format(
        path_blender_executable, blend_file_full_path, python_script_full_path
    )
    os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-blender", type=str, default="/opt/blender-3.0.0/blender")
    parser.add_argument("-s", type=str, default=None)
    args = parser.parse_args()

    path_blender_executable = args.blender

    dirname = os.path.dirname(__file__)

    if args.s is None:
        for name, (python_script, blend_file) in TESTS.items():
            run(name, path_blender_executable, python_script, blend_file)
    else:
        python_script, blend_file = TESTS[args.s]
        run(args.s, path_blender_executable, python_script, blend_file)
