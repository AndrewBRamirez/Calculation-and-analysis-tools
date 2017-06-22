# This program learns and stores molecular masses of elements and consequently
# calculates molecular masses of compounds

        
def get_elements(filename='EMMLibrary.txt'):
    """
    :param filename: a string representing the filename for the library of
    elements that have already been stored
    :return: a dictionary with elements as keys and their molar masses as values
    """

    # List to be populated with elements from the library
    element_dict = {}
    
    # Open a file to read
    file = open(filename, 'r')

    # Search each line
    for line in file:
        
        # Save the element and its molar mass in the dictionary
        element_dict[line[:line.index(',')]] = float(line[line.index(',') + 1:])
    
    # Close the file
    file.close()
    
    return element_dict


def add_to_library(element, value, filename='EMMLibrary.txt'):
    """
    :param element: the abbreviation of the element to be added
    :param value: the molecular mass for the given element
    :param filename: the file name for the library storing the molar masses
    :return: None
    """
    
    # Open the file
    fh = open(filename, "a")
    
    # Create and add a new entry
    add_entry = '%s,%s' % (element, value)
    fh.write(add_entry + '\n')
    
    # Close the file once done
    fh.close()

# Start the main executable portion of the program
if __name__ == '__main__':
    
    # Define local variables
    
    # Dictionary used to store used elements and their molar masses
    elements = get_elements()

    # The cumulative molar mass of the compound
    mm = 0
    
    # Dict storing the elements in the current molecule
    molecule = {}
    
    # User control loop which gets conditionally broken out of from within
    while True:
        
        # Prompt user for an element
        entry = input('Please enter the element abbreviation and the number of '
                      'atoms of that element, or \"done\" if no more elements '
                      'to be added;\nalternatively, you may enter the name '
                      'of a molecule in lower case and see if the library has '
                      'it:\n')
        
        # Separate entry into the two main pieces of information
        entry = entry.split()
        
        # Check if the user is finished adding elements
        if entry[0].lower() == 'done':
            break
        
        # Tell the user the value was found and add it to the molecule
        if entry[0] in elements.keys():
            print('We found that element in the library!\n')
            
            # Save the molar mass and number of atoms present
            molecule[entry[0]] = (elements[entry[0]], entry[1])
        
        # Notify the user the element wasn't found and handle adding it
        else:
            print('We didn\'t find that element in the library; we\'ll add it '
                  'for you:')
            add_info = input('What is the molar mass of the element %s?\n'
                             % entry[0])
            add_to_library(entry[0], add_info)
            
            print('Got it.\n')
            
            # Add the element to the dictionary used in the main loop as well
            # as the current molecule
            molecule[entry[0]] = (add_info, entry[1])
            
    # Sum all contributions
    for atom in molecule:
        mm += float(molecule[atom][0]) * float(molecule[atom][1])
    
    # Print the result
    print('%g grams per mole is the molar mass of your compound.' % mm)

    want_moles = input('Would you like to calculate the amount of moles in '
                       'your sample?\n')
    
    # Calculate moles in the compound, if the user wishes
    if want_moles[:2].lower() != 'no':
        grams = float(input('Please enter the amount of grams of your '
                            'compound:\n'))

        # Calculate total moles and print the result
        total_moles = grams / mm
        print('You have %g moles in total of your compound.' % total_moles)
    else:
        print('Goodbye!')
