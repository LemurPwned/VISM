from data_assembly import Assembly

if __name__ == "__main__":
    directory = "data\\0200nm"
    assembler = Assembly(directory)
    omf_files, odt_file = assembler.read_simulation_files()
    data, base_data = assembler.process_simulation_files(omf_files=omf_files,
                                                            filetype='binary')
    
