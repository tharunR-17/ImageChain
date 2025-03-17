from imagechain import *

ans="y"
imgChain=ImageChain()
if not imgChain.chain:
    imgChain.create_genesis_block("mypic1.jpg")
else:
    print("Loaded existing blockchain from MongoDB.")

imgChain.add_block("ARamesh_photo.jpg")
    # imagechain.add_block("sample2.jpg")
while ans=="y":
    imgChain.chain = imgChain.load_from_mongodb()
    if imgChain.verify_chain_real_time():
        print("\n✅ ImageChain is valid.\n")
    else:
        print("\n❌ ImageChain is corrupted.\n")
    ans=input("Do you want to create a new block? (y/n): ")