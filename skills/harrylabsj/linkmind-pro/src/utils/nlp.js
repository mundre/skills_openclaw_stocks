/**
 * nlp.js - 文本规范化工具
 */

const STOPWORDS = new Set([
  'the','and','for','that','this','with','from','into','your','have','will','not','are','was','were','can','could','should','about','what','when','where','which','while','than','then','them','they','their','there','here','also','more','most','some','such','using','used','use','make','made','over','under','very','just','only','each','been','being','does','did','done','how','why','our','you','its','his','her','she','him','who','has','had','but','too','via','per','one','two','three',
  '我们','你们','他们','这个','那个','一个','一种','可以','需要','如果','因为','所以','以及','进行','通过','没有','不是','就是','如何','什么','为什么','时候','今天','已经','还有','对于','一些','这种','那些','并且','或者','主要','用户','系统','功能','能力','作为','实现','相关','用于'
]);

function normalizeConcept(text) {
  if (!text) return '';
  return text
    .toLowerCase()
    .replace(/[\u2018\u2019'"""''()（）【】\[\],.:;!?/\\]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

module.exports = { normalizeConcept, STOPWORDS };
