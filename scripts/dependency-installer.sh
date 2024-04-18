sudo apt update; sudo apt-get -y install make docker build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
curl -sS https://pyenv.run | bash
echo '
# pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
' >> ~/.bashrc
sudo pyenv install 3.11.1 && pyenv local 3.11.1
pip install -U pip && pip install poetry
poetry config virtualenvs.in-project true
