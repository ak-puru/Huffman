import bitio
import huffman
import pickle


def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''
    return pickle.load(tree_stream)


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    reached_byte = False

    while not reached_byte:
        code = bitreader.readbit()
        if code == 1:
            tree = tree.getRight()
        elif code == 0:
            tree = tree.getLeft()
            
        if isinstance(tree, huffman.TreeLeaf):
            reached_byte = True
            return tree.getValue()


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''

    try:
        tree = read_tree(compressed) #creating the tree
    except:
        return

    bitread  = bitio.BitReader(compressed)
    bitwrite = bitio.BitWriter(uncompressed)

    try:
        decode = decode_byte(tree, bitread) #decoding file bits
    except EOFError:
        decode = None

    while decode != None: #writing bits if there is no EOFError
        try:
            bitwrite.writebits(decode, 8)
            decode = decode_byte(tree, bitread)
        except EOFError: 
            decode = None


def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Hint:  Use pickle.dump()
    **Requirement:**  pickle.dump(..., protocol=4)

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''
    pickle.dump(tree, tree_stream, protocol=4)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    
    try:
        write_tree(tree, compressed)
    except:
        return
    
    hash_table = huffman.make_encoding_table(tree)
    bitread    = bitio.BitReader(uncompressed)
    bitwrite   = bitio.BitWriter(compressed)

    reached_eof= False

    while not reached_eof:
        try:
            byte = bitread.readbits(8)
            code = hash_table[byte]
            for bit in code:
                bitwrite.writebit(bit)

        except EOFError:
            reached_eof = True
            code = hash_table[None]
            for bit in code:
                bitwrite.writebit(bit)

    bitwrite.flush()
