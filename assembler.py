import os
import subprocess
import sys
import pass1
import pass2


def launch_gui():
    project_root = os.path.dirname(os.path.abspath(__file__))
    gui_script = os.path.join(project_root, "gui", "gui.py")
    subprocess.Popen([sys.executable, gui_script], cwd=project_root)


def main(input_file="input.asm"):
    pass1.readf(input_file)
    pass1.pass1()
    pass1.print_pool_table()
    pass1.print_symbol_table()
    pass1.write_intermediate_file()
    pass1.write_symbol_table_file()
    pass1.write_pool_table_file()
    pass1.write_block_table_file()
    pass2.main()
    launch_gui()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.asm")
    