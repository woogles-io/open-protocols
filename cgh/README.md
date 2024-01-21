# Impetus

The impetus for creating a new format for crossword game representation is manyfold.

GCG, while it has worked fantastically for spreading representations of our game
via the Internet and for analysis purposes,
has a few issues. Since it's not 100% strictly specified, implementers do several
things differently. For example, playthrough tiles are `.`, `(A)`, or the actual letter,
depending on the implementer. Lexicons and rules are not encoded in the format by default.

The format specifies how to represent unknown tiles being exchanged, but many implementers
do not support this. This is more of an implementation issue, however. Still, many hacks
are used such as `-IIII`, for example.


There are also some issues:

1) UTF-8 is not native to the format, but it actually uses another encoding natively
2) Multiline comments are not natively supported
3) Situations like overdraws, misscores, etc are not supported
4) Time remaining is not supported
5) Variants, different board layouts and tile distributions, etc are not supported


Mainly, we would love to have a format that is as unambiguous and well-specified
as possible. It should also be easy to edit with a standard text editor.

We would also like to ship a validator, hopefully in a few languages.


# Protobuf

Protobuf is a good way of declaring a format that can later be extended without losing
backwards compatibility. However, the format should also be easy to edit by hand,
and native Protobuf does not make this possible.

protojson is a possibility, but JSON is not friendly to edit by hand.

prototext is a possibility, we can see how this looks.

**YAML** is currently preferred, but we must take care to use a good converter, since
there will be a double conversion (proto -> JSON -> YAML).

Parsers should use our protobuf file and generated code for best compatibility.

See `cgh.proto` in this directory for the Protobuf file that describes our specification.

# Examples





# protoc

`protoc --go_out=./cgh/impl/gen --go_opt=paths=source_relative ./cgh/cgh.proto`