
EBAY SELLER SCRAPER

1) Download and install Google Chrome in Linux terminal (or WSL): 

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb


2) Install Python3:

sudo apt install python3 python3-pip ipython3

3) Install pip:

sudo apt -y purge python-pip
sudo python -m pip uninstall pip
sudo apt -y install python-pip
pip install --upgrade pip
echo "export PATH=\"${HOME}/.local/bin:$PATH\"" >>"${HOME}"/.bashrc

3) Install dependencies:

pip install selenium
pip install pandas
pip install requests

4) Run the script: 

python3 scrape.py "iphone 11 pro max"
