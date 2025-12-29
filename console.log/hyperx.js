var hyperx = require('hyperx')

var convertTaggedTemplateOutputToDomBuilder = hyperx(function (tagName, attrs, children) {
  console.log(tagName, attrs, children)
})

convertTaggedTemplateOutputToDomBuilder`<h1>hello world</h1>`

// Running this produces: h1 {} [ 'hello world' ]
