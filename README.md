# nshash
using top-n longest sentences' hashes as document's n fingerprints to identify similar documents.
对一篇文章的最长n句话分别计算hash值，作为该文章的n个指纹，两篇文章只要有一个指纹相同就认为这两篇文章相同，从而达到文章去重的目的。

# 使用方法
```python
import nshash

nsh = nshash.NSHash(name='test', hashfunc='farmhash', hashdb='memory')

similar_id = nsh.get_similar(doc_text)
```

`NShash`类有三个参数：
+ `name`： 用于hashdb保存到硬盘的文件名，如果hashdb是HashDBMemory, 则用pickle序列化到硬盘；如果是HashDBLeveldb，则leveldb目录名为：name+'.hashdb'。name按需随便起即可。
+ `hashfunc`: 计算hash值的具体函数类别，目前实现两种类型：`md5`和`farmhash`。默认是`md5`，方便Windows上安装farmhash不方便。
+ `hashdb`：默认是`memory`即选择HashDBMemory，否则是HashDBLeveldb。

如果你想用Redis或MySQL等其它数据库来实现HashDB，可以参照HashDBLeveldb、HashDBMemory进行实现。

至于如何利用similar_id进行海量文本的去重，这要结合你如何存储、索引这些海量文本。可参考`example/test.py`文件。这个test是对excel中保存的新闻网页进行去重的例子。


# 算法原理

文章去重（或叫网页去重）是搜索引擎非常关心的一个问题。搜索引擎中抓取的网页是海量的，海量文本的去重算法也出现了很多，比如minihash, simhash等等。

在工程实践中，对simhash使用了很长一段时间，有些缺点，一是算法比较复杂、效率较差；二是准确率一般。

网上也流传着百度采用的一种方法，用文章最长句子的hash值作为文章的标识，hash相同的文章（网页）就认为其内容一样，是重复的文章（网页）。

这个所谓的“百度算法”对工程很友好，但是实际中还是会有很多问题。中文网页的一大特点就是“天下文章一大抄”，各种博文、新闻几乎一字不改或稍作修改就被网站发表了。这个特点，很适合这个“百度算法”。但是，实际中个别字的修改，会导致被转载的最长的那句话不一样，从而其hash值也不一样了，最终结果是，准确率很高，召回率较低。

为了解决这个问题，我提出了nshash算法，即：去文章的最长n句话（实践下来，n=5效果不错）分别做hash值，这n个hash值作为文章的指纹，就像是人的5个手指的指纹，每个指纹都可以唯一确认文章的唯一性。这是对“百度算法”的延伸，准确率还是很高，但是召回率大大提高，原先一个指纹来确定，现在有n个指纹来招回了。

# 算法实现
该算法的原理简单，实现起来也不难。比较复杂一点的是对于一篇文章（网页）返回一个similar_id，只要该ID相同则文章相似，通过groupby similar_id即可达到去重目的。

为了记录文章指纹和similar_id的关系，我们需要一个key-value数据库，本算法实现了内存和硬盘两种key-value数据库类来记录这种关系：

+ HashDBLeveldb 类：基于leveldb实现, 可用于海量文本的去重；
+ HashDBMemory  类：基于Python的dict实现，可用于中等数量（只要Python的dict不报内存错误）的文本去重。

从效率上看，肯定是HashDBMemory块了。利用nshash对17400篇新闻网页的测试结果如下:

+ HashDBLeveldb: 耗时2.47秒；
+ HashDBMemory: 耗时1.6秒；

具体测试代码请看 `example/test.py`。


