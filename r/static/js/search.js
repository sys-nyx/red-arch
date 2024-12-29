let idxs = new XMLHttpRequest();
idxs.open('GET', '/static/js/search/search-idx-list.json', false);
idxs.send();
let idx_list =JSON.parse(idxs.responseText);

let lnrjs = new XMLHttpRequest();
lnrjs.open('GET', '/static/js/lunr.js', false);
lnrjs.send();
eval(lnrjs.responseText);


let meta = new XMLHttpRequest();
meta.open('GET', '/static/js/search/metadata.json', false);
meta.send();
var metadata = JSON.parse(meta.responseText)


async function getData(element) {
    const url = `/${element}`;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }
  
      const json = await response.json();
      return json
    } catch (error) {
      console.error(error.message);
    }
  }

onmessage = (e) => {
    let query = e.data
    let results = []
    idx_list.forEach(element => {
        p = getData(element)
        p.then(function (json) {
            let idx = lunr.Index.load(json)
            res = idx.search(query).slice(0,100)
            res.forEach(r => {
              r.meta = metadata[r.ref]
            })
            results = results.concat(res)
            results = results.sort(({score:a}, {score:b}) => b-a);
            results = results.slice(0,100)
            postMessage(results)
        })
        // let request = new XMLHttpRequest();
        // request.open('GET', `/${element}`, false);
        // request.send();
        // console.log(JSON.parse(request.responseText))
        // let idx = lunr.Index.load(JSON.parse(request.responseText))
        // res = idx.search(query).slice(0,100)
        // results = results.concat(res)
        // results = results.sort(({score:a}, {score:b}) => b-a);
        // results = results.slice(0,100)
        // postMessage(results)
        
    })
}
