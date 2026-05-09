import pass1
import pass2
import sys

def main(*argv):
    input_file = argv[1] if len(argv) > 1 else "input.asm"
    pass1.readf(input_file)
    pass1.pass1()
    pass1.print_pool_table()
    pass1.print_symbol_table()
    pass1.write_intermediate_file()
    pass1.write_symbol_table_file()
    pass1.write_pool_table_file()
    pass1.write_block_table_file()
    pass2.main()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.asm")
    