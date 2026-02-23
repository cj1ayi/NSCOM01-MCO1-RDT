# DEBUG VERSION
This version is basically RDTP but with some edits made to the code for the purpose of showing the programs response when faced with: a checksum mismatch error, slow packet delivery (need for retransmission), and with not enough diskspace.

The debug responses are triggered based on what files are uploaded (all edits were done on client-side). Below is a list of the files and what they do:
**checksum.pdf** -- Causes a checksum mismatch error when uploaded
**snail.jpeg** -- Has a 7 second delay before sending data packets when being uploaded. Makes it so that the server will need to do a retransmission
**fakegeronimo.txt** -- The WRQ will change the filesize to 1TB (the file itself is not actually 1TB), causing an error stating that there is not enough space.
