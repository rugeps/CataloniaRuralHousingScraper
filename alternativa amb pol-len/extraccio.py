from pdfrw import PdfReader


pdf_file_location = 'XAC-52-2019_02-2020.pdf'


if __name__ == '__main__':
    # Reads pdf
    x = PdfReader(pdf_file_location)

    # print(x.keys())
    # print(x.Info)
    # print(x.Root.keys())
    # len(x.pages)
    # x.pages[0]
    # x.pages[0].Contents

    bytestream = x.pages[0].Contents.stream
    print(bytestream)