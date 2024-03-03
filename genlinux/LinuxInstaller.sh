LCHOME=$HOME/lucaschess
mkdir $LCHOME
cd $LCHOME

echo
echo DOWNLOAD Lucas Chess sources from GitHub
echo
git clone https://github.com/lukasmonk/lucaschessR2.git

echo
echo MINICONDA3 installation
echo
wget -O miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-py38_23.11.0-2-Linux-x86_64.sh
sh ./miniconda3.sh -b -p $HOME/lucaschess/miniconda3

export PATH=$LCHOME/miniconda3/bin:$PATH
conda install -c conda-forge pyside2

echo
echo PYTHON LIBRARIES installation
echo
pip3 install -r ./lucaschessR2/requirements.txt

cd lucaschessR2/bin/OS/linux
sh ./RunEngines

cd $LCHOME

echo "export PATH=$LCHOME/miniconda3/bin:$PATH" >  LucasR.sh
echo "export QT_LOGGING_RULES='*=false'" >> LucasR.sh
echo "export XDG_SESSION_TYPE=xcb" >> LucasR.sh
echo "cd lucaschessR2/bin" >> LucasR.sh
echo "python LucasR.py" >> LucasR.sh
chmod +x LucasR.sh
echo
echo Created in $LCHOME LucasR.sh to launch the program

echo
echo "cd lucaschessR2" > update_lucaschess.sh
echo "git pull" >> update_lucaschess.sh
echo "cd bin/OS/linux" >> update_lucaschess.sh
echo "sh ./RunEngines" >> update_lucaschess.sh
chmod +x update_lucaschess.sh
echo
echo Created in $LCHOME update_lucaschess.sh to update the program from sources in GitHub



