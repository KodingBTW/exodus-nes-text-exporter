# Exodus - Journey to the Promised Land text extractor
# Source code by koda
# Version 1.0 - 28-10-2024

import sys
import os

def readRom(romFile, startOffset, endOffset):
    """
    Reads a segment of the ROM file from startOffset to endOffset.
    
    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The starting position in the file to read from.
        endOffset (int): The ending position in the file to read to.
    
    Returns:
        bytes: The data read from the ROM file.
    """
    with open(romFile, "rb") as f:
        f.seek(startOffset)
        data = f.read(endOffset - startOffset)
    return data

def processPointers(data, offset):
    """
    Processes the pointer data by reversing byte pairs and adding a specified offset.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        offset (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    for i in range(0, len(data), 2):
        pair = data[i:i + 2][::-1]  # Reverse byte pair
        value = int.from_bytes(pair, byteorder='big')  # Convert to integer
        newValue = value + offset  # Add the distance between pointer and text
        result.append(newValue)
    return result

def extractTexts(romData, addresses):
    """
    Extracts texts from the ROM data at specified addresses until a text breaker is encountered.
    
    Parameters:
        romData (bytes): The complete ROM data.
        addresses (list): A list of addresses to read the texts from.
    
    Returns:
        tuple: A list of extracted texts and the total bytes read.
    """
    texts = []
    totalBytesRead = 0  # Counter for bytes read
    textBreakers = {0x04, 0x05, 0x06, 0x07}  # Text Breaker bytes
    for addr in addresses:
        text = bytearray()  # To hold the extracted text
        while True:
            byte = romData[addr]
            totalBytesRead += 1  # Count the byte read
            if byte in textBreakers:  # Stop at the breaker
                breakerByte = byte
                break
            text.append(byte)  # Add byte to text
            addr += 1

        # Add the breaker byte to the text
        if breakerByte is not None:
            text.append(breakerByte)  # Append the breaker byte
        texts.append(text.decode('utf-8', errors='ignore'))  # Convert to string
    return texts, totalBytesRead


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stdout.write("Usage: python <script_name.py> <romFile.nes> <outFile.txt>\n")
        sys.exit(1)
        
    # IMPORTANT OFFSETS (DON'T TOUCH)
    POINTERSSTARTOFFSET = 0x144F4       # Table pointers first offset.
    POINTERSENDOFFSET = 0x146E8         # Table pointers last offset.
    POINTERSDISTANCE = 0x8010           # Text offset - Inverted Pointer.

    romFile = sys.argv[1]  # The ROM file path from command line argument
    outFile = sys.argv[2]  # The output text file path from command line argument

    # Read ROM pointers table.
    tablePointers = readRom(romFile, POINTERSSTARTOFFSET, POINTERSENDOFFSET)

    # Process read pointers
    textPointers = processPointers(tablePointers, POINTERSDISTANCE)

    # Read the complete ROM data to extract texts
    romData = readRom(romFile, 0, os.path.getsize(romFile))

    # Extract the texts
    texts, totalBytesRead = extractTexts(romData, textPointers)

    # Writing the content to a text file
    with open(outFile, "w", encoding='utf-8') as f:
        # Write the total bytes read in the first line
        f.write(f"{totalBytesRead}\n")
        for text in texts:
            f.write(f"{text}\n")
    print(f"Text extracted to {outFile}.")
    print(f"Total: {totalBytesRead} bytes read.")
