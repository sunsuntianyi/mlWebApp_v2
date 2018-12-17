#!/usr/bin/env python

import os
import re
import tempfile
import shutil
import sys
import subprocess
import zipfile

# Return True if running on Windows
def IsWindows():
  return os.name == 'nt'

def GetWindowsPathWithUNCPrefix(path):
  """
  Adding UNC prefix after getting a normalized absolute Windows path,
  it's no-op for non-Windows platforms or if running under python2.
  """
  path = path.strip()

  # No need to add prefix for non-Windows platforms.
  # And \\?\ doesn't work in python 2
  if not IsWindows() or sys.version_info[0] < 3:
    return path

  # Lets start the unicode fun
  unicode_prefix = "\\\\?\\"
  if path.startswith(unicode_prefix):
    return path

  # os.path.abspath returns a normalized absolute path
  return unicode_prefix + os.path.abspath(path)

PYTHON_BINARY = 'python'
if IsWindows() and not PYTHON_BINARY.endswith('.exe'):
  PYTHON_BINARY = PYTHON_BINARY + '.exe'

# Find a file in a given search path.
def SearchPath(name):
  search_path = os.getenv('PATH', os.defpath).split(os.pathsep)
  for directory in search_path:
    if directory == '': continue
    path = os.path.join(directory, name)
    if os.path.isfile(path) and os.access(path, os.X_OK):
      return path
  return None

def IsRunningFromZip():
  return False

# Find the real Python binary if it's not a normal absolute path
def FindPythonBinary(module_space):
  if PYTHON_BINARY.startswith('//'):
    # Case 1: Path is a label. Not supported yet.
    raise AssertionError(
      'Bazel does not support execution of Python interpreters via labels yet')
  elif PYTHON_BINARY.startswith('/'):
    # Case 2: Absolute path.
    return PYTHON_BINARY
  elif '/' in PYTHON_BINARY:
    # Case 3: Path is relative to the repo root.
    return os.path.join(module_space, PYTHON_BINARY)
  else:
    # Case 4: Path has to be looked up in the search path.
    return SearchPath(PYTHON_BINARY)

def CreatePythonPathEntries(python_imports, module_space):
  parts = python_imports.split(':');
  return [module_space] + ["%s/%s" % (module_space, path) for path in parts]

# Find the runfiles tree
def FindModuleSpace():
  stub_filename = os.path.abspath(sys.argv[0])
  module_space = stub_filename + '.runfiles'
  if os.path.isdir(module_space):
    return module_space

  runfiles_pattern = "(.*\.runfiles)/.*"
  if IsWindows():
    runfiles_pattern = "(.*\.runfiles)\\.*"
  matchobj = re.match(runfiles_pattern, os.path.abspath(sys.argv[0]))
  if matchobj:
    return matchobj.group(1)

  raise AssertionError('Cannot find .runfiles directory for %s' % sys.argv[0])

# Create the runfiles tree by extracting the zip file
def CreateModuleSpace():
  ZIP_RUNFILES_DIRECTORY_NAME = "runfiles"
  temp_dir = tempfile.mkdtemp("", "Bazel.runfiles_")
  zf = zipfile.ZipFile(GetWindowsPathWithUNCPrefix(os.path.dirname(__file__)))
  zf.extractall(GetWindowsPathWithUNCPrefix(temp_dir))
  return os.path.join(temp_dir, ZIP_RUNFILES_DIRECTORY_NAME)

# Returns repository roots to add to the import path.
def GetRepositoriesImports(module_space, import_all):
  if import_all:
    repo_dirs = [os.path.join(module_space, d) for d in os.listdir(module_space)]
    return [d for d in repo_dirs if os.path.isdir(d)]
  return [os.path.join(module_space, "tf_serving")]

def Main():
  args = sys.argv[1:]

  new_env = {}

  if IsRunningFromZip():
    module_space = CreateModuleSpace()
  else:
    module_space = FindModuleSpace()

  python_imports = 'protobuf_archive/python'
  python_path_entries = CreatePythonPathEntries(python_imports, module_space)
  python_path_entries += GetRepositoriesImports(module_space, True)

  python_path_entries = [GetWindowsPathWithUNCPrefix(d) for d in python_path_entries]

  old_python_path = os.environ.get('PYTHONPATH')
  python_path = os.pathsep.join(python_path_entries)
  if old_python_path:
    python_path += os.pathsep + old_python_path

  if IsWindows():
    python_path = python_path.replace("/", os.sep)

  new_env['PYTHONPATH'] = python_path

  # Now look for my main python source file.
  # The magic string percent-main-percent is replaced with the filename of the
  # main file of the Python binary in BazelPythonSemantics.java.
  rel_path = 'inception_client.py'
  if IsWindows():
    rel_path = rel_path.replace("/", os.sep)

  main_filename = os.path.join(module_space, rel_path)
  main_filename = GetWindowsPathWithUNCPrefix(main_filename)
  assert os.path.exists(main_filename), \
         'Cannot exec() %r: file not found.' % main_filename
  assert os.access(main_filename, os.R_OK), \
         'Cannot exec() %r: file not readable.' % main_filename

  program = python_program = FindPythonBinary(module_space)
  if python_program is None:
    raise AssertionError('Could not find python binary: ' + PYTHON_BINARY)
  args = [python_program, main_filename] + args

  os.environ.update(new_env)

  try:
    sys.stdout.flush()
    if IsRunningFromZip():
      # If RUN_UNDER_RUNFILES equals 1, it means we need to
      # change directory to the right runfiles directory.
      # (So that the data files are accessible)
      if os.environ.get("RUN_UNDER_RUNFILES") == "1":
        os.chdir(os.path.join(module_space, "tf_serving"))
      retCode = subprocess.call(args)
      shutil.rmtree(os.path.dirname(module_space), True)
      exit(retCode)
    else:
      os.execv(args[0], args)
  except EnvironmentError:
    # This works from Python 2.4 all the way to 3.x.
    e = sys.exc_info()[1]
    # This exception occurs when os.execv() fails for some reason.
    if not getattr(e, 'filename', None):
      e.filename = program  # Add info to error message
    raise

if __name__ == '__main__':
  Main()
