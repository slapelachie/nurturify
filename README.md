# Nurturifier
A simple script to convert images to resemble the style of Porter Robinson's nurture.

## Example
This an example output through the command `$ nurturify -i test.png -t left_vertical`
![Example output](/git_resources/example.png)

## Installation
Tested on Arch Linux and nothing else. This probably works on other distros as well.
### Prerequisites
#### Python Modules
Idk what modules are installed by default, I'll get to this one day

### Installing
In the root folder (where this README is) issue  the command `$ make && make install && make clean`. This allows for a quick install of the program. Edit the make file to suit your needs if needed.

Place the fonts found under `/assets/fonts/` into your `~/.fonts/` directory.

## How to use
If you ever forget the syntax used for this script, use nurturify -h for the entire syntax.

### Syntax
The arguments are the following

| Argument  | Usage |
|-----------|-----------------------------------------------------|
| -h, --help| Shows the help message |
| -i        | The input file |
| -o        | The output file |
| -t        | The type of cut (TOP_HORIZONTAL, BOTTOM HORIZONTAL, LEFT_VERTICAL, RIGHT_VERTICAL)
| -c        | The abount to take away in percentage (e.g. 30 for 30%)|
| -v        | Verbose logging |

## License
Using the [GNU GPL](LICENSE) license
