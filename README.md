# Ever17 Scenario Scripts
This is a dump of the various scripts used to unpack, edit, and recompile the [Ever17](https://vndb.org/v17) script used in the [Himmel Edition](https://vndb.org/r60521) patch.

This was built for a specific workflow that involved editors modifying the script in Google Sheets. I did not want them to accidentally alter anything other than the text, so this was made in a certain way. I was only interested in making it work, not necessarily streamlining the process, so **there's some hardcoded path and directories in the scripts**. Feel free to modify them and use for your own purposes.

This also contains tools to check for duplicated text and text that's common between routes. This was done to make translations consistent, and also to allow skipping common text using a modified game executable.

**Note: It is IMPORTANT that you save all text files as ANSI**. UTF-8 or any other encoding will break the game.

## Usage
1. Dump the SCR files from the PC version. This can be done by running the [AnimEd](https://github.com/niksaak/ae) ([binaries](http://wks.arai-kibou.ru/ae.php?p=dl)) "Archive Tool".
2. Use the AnimEd "E17 SCR tool" to open the scenarios and export data chunks. Make sure to decode and keep all opcodes. Make sure your files are structured as `<dir_scr_extracted>/<filename>/<filename>.scr_chunk_*`
3. At some point I converted the ".scr_chunk" files to plaintext and uploaded to Google Sheets for the editors to modify, but I lost the tool I used for that. I included these plaintext files in this repository in the `text/in` directory.
4. Modify the txt files in `text/in` as needed.
5. Run **break_and_merge.py**, making sure that `dir_scr_original` is set to the value of "dir_scr_extracted" from step 2 and `path_output_dat` is the location of the script.dat file you'd like to output.

## SCR File Structure
For information about how the Ever17 SCR files work as well as their file specifications, visit [SCR_format.md](SCR_format.md)

## Tools
- **break_and_merge.py**: Goes through the "in" folder, reads the text, appropriately centers anything in the centering tags, and replaces newlines with the appropriate command to prepare for compilation. Writes this to the "out" folder. It then converts all files in the "out" folder to ".scr_chunk" files, then packs them into the final SCR file.
- **decompress_cps.py**: Decompress and unobfuscate CPS files. This is mostly used in images. To convert an image back into a CPS file, check out the [Ever17 CPS Converter](https://github.com/arsym-dev/Ever17-CPS-Converter).

### Debugging
- **scan_for_formatting_tokens.py**: Prints formatting tokens to the console
- **scan_for_unsupported_tokens.py**: Prints undocumented tokens/arguments to the console

### Quality of life
- **duplicate_check.py**: This would go through each file in the "duplicate_check" folder and check if two files had the same Japanese text but different English text. It would print this instances to the console.
- **duplicate_check2.py**: The same thing as duplicate_check.py but more refined and with additional constraints to only match longer lines. This avoids a thousand matchs for "Huh?"
- **offset_calculator.py**: This was used to modify the EXE and determine what the correct address for each chunk was.

### Obsolete
- **linebreak.py**: The precursor to "break_and_merge.py". Goes through the "in" folder, reads the text, appropriately centers anything in the centering tags, and replaces newlines with the appropriate command to prepare for compilation.
- **merge_tl_into_script.py**: This seems to be similar to "break_and_merge.py", but it combines data from the original .src_chunk files and creates new .src_chunk files. I think I created this when I was still relying on AnimEd to recombile the chunks back into an SCR file. I would use "break_and_merge.py" in most cases.