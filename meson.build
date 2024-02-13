project('zeyphr-toolchain', 'c',
  default_options : ['warning_level=3'])

py3_mod = import('python')
py3_inst = py3_mod.find_installation('python3')
if py3_inst.language_version().version_compare('<3.10')
  error('At least Python 3.10 is required.')
endif

# setup west
west = find_program('west', required: false)
west_env = ''
if not west.found()
  if get_option('offline')
    error('west tool not found and not allowed to download it (offline is set).')
  endif
  west_dir = meson.current_build_dir() / 'west'
  west = find_program(west_dir / 'bin' / 'west', required: false)
  west_env = 'PYTHONPATH=' + west_dir
  if not west.found()
    py3_inst = py3_mod.find_installation('python3', modules: 'pip')
    run_command(py3_inst, '-m', 'pip', 'install', f'--target=@west_dir@', 'west', check: true)
    west = find_program(west_dir / 'bin' / 'west')
  endif
endif

# setup zephyr
zephyr = subproject('zephyr')
zephyr_source_dir = zephyr.get_variable('source_dir')
zephyr_work_dir = meson.current_build_dir() / 'zephyr'
r = run_command(
  py3_inst, files('setup-zephyr.py'),
  '--rtos-dir', zephyr_source_dir,
  '--working-dir', zephyr_work_dir,
  'check',
  check: false
)
if r.returncode() != 0
  if get_option('offline')
    r = run_target(
      command: [py3_inst, files('setup-zephyr.py'),
      '--rtos-dir', zephyr_source_dir,
      '--working-dir', zephyr_work_dir,
      '--west-path', west.full_path(),
      '--west-env', west_env,
      'init']
    )
    error('Zephyr working directory not initialized. Run "meson compile init-zephyr for that."')
  endif
  message('Initialize Zephyr repos (west init/west update). This may take a long time.')
  r = run_command(
    py3_inst, files('setup-zephyr.py'),
    '--rtos-dir', zephyr_source_dir,
    '--working-dir', zephyr_work_dir,
    '--west-path', west.full_path(),
    '--west-env', west_env,
    'init',
    check: true
  )
endif
