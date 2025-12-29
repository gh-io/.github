var React = require('react')
var toString = require('react-dom/server').renderToString
var hyperx = require('hyperx')
var hx = hyperx(function createElement (component, properties, children) {
  // Pass children as separate arguments to avoid key warnings
  return React.createElement.apply(null, [component, properties].concat(children))
}, {
  createFragment: function createFragment (children) {
    return React.createElement.apply(null, [React.Fragment, {}].concat(children))
  }
})

var title = 'world'
var wow = [1,2,3]
var frag = hx`
  <tr> <td>row1</td> </tr>
  <tr> <td>row2</td> </tr>
`
var tree = hx`<div>
  <h1 y="ab${1+2}cd">hello ${title}!</h1>
  ${hx`<i>cool</i>`}
  wow
  ${wow.map(function (w, i) {
    return hx`<b>${w}</b>\n`
  })}

  <table>${frag}</table>
</div>`
console.log(toString(tree))
