Webカメラからリアルタイムの認識  
手書き文字のリアルタイムの認識  
手持ちの画像の認識  
などのツールキットです．  

###動作環境（私の）

`python 2.7.12`  
`chainer 1.17.0`  
`openCV 2.4.12`  
`numpy 1.10.4`  
`PIL 3.4.1`  
`matplotlib 1.5.3`  

これらは自分で入れてください．それはできるよね？

#始めに

学習に使用する画像を用意します．  
それらをカテゴリに分けて，それぞれ別のディレクトリに入れてください．  
例：
tanaka-  
　　　|-t1.jpg, t2.jpg, t3.jpg  
suzuki-  
　　　|-s1.jpg, s2.jpg, s3.jpg  
それをPictureディレクトリにぶちこんでください．
例：
Picture--  
　　　　|-tanaka, suzuki  

終わったら次を実行

`$python preprocess.py`

これで学習を行う準備が整います．  
256×256に変換された画像が入る`Images`, `Images_row`ディレクトリ  
学習に使用する画像の場所が書かれたtrain.txt  
評価に使用する画像の場所が書かれたtest.txt  
あとでいろいろ使えるlabels.txt  
平均画像が保存されたmean.npy  

これがちゃんと実行されれば下を実行して実際の学習を始めましょう．  
-E 10 となっている部分を-E 100とかに変えればもっとたくさん学習できます．  

`python train_imagenet.py -g 0 -E 10 train.txt test.txt`  

完成したmodel.modelを使って，  
Webカメラからリアルタイムの認識に使える camera.py  
リアルタイムの手書き文字の認識などに使える tegaki.py  
手持ちの画像の認識に使える inspection.py  
が使えるようになります．  

##Webカメラからリアルタイムの認識

同一ディレクトリにOpenCVのcascadeファイルを用意し，cascade.xmlにリネーム  

`$python camera.py`

で実行．もちろんWebカメラをPCにセットしてくださいね．  

##手書き文字のリアルタイムの認識

`$python tegaki.py`

で手書きのためのWindowが出ますので，そこにマウスなどで書き込んでください．  
eで今書いている文字を消去  
qでプログラムを終了できます．  

##手持ちの画像の認識

`$python inspection.py [image.jpg]`

[image.jpg]の部分は認識したい画像の名前で置き換えてください．  
こういうところを理解してもらえないことが多いので例を書きます．  

例：  
`$python inspection.py t1.jpg`
`$python inspection.py pikachu.png`
`$python inspection.py trump.jpeg`



それと，使うことも少ないだろうとは思いますが，  
Pictureディレクトリと同じような構成で  
testPictureを用意し，  

`$python check.py testPicture/`

を実行すると，testPictureディレクトリ内の画像をまとめて認識してくれます．  
これはサクッとディープラーニングくんのimenurokさんhttp://qiita.com/imenurok/items/fecc9ca8d96eb623aaefが作ってくださったものに近いのですが，  
imenurokさんのcheck.pyはカラー画像に対応していません．（実行はできますが，PILとOpenCVのnumpy配列の違いを意識していないので，認識率が超低くなります．）  

以上です．  
