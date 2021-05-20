wget "http://images.cocodataset.org/zips/val2017.zip"
wget "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
mkdir -p data
unzip val2017.zip -d data/
rm val2017.zip
unzip annotations_trainval2017.zip -d data/
rm annotations_trainval2017.zip
