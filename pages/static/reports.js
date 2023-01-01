function get_reports() {
  fetch(`https://api.freasearch.org/search?q=misskey`)
  .then(function (data) {
    return data.json();
  })
  .then(function (api_result) {
    console.log(api_result);

    for (var i = 0; i < api_result.results.length; i++) {
      var div = document.createElement('div');
      div.className = 'report-text';

      var link = document.createElement('a');
      link.href = api_result.results[i].url;


      var title = document.createElement('h3');
      title.textContent = api_result.results[i].parsed_url[1];

      var context = document.createElement('p');
      context.textContent = api_result.results[i].content;

      link.appendChild(title);
      div.appendChild(link);
      div.appendChild(context);
      document.getElementById('reports').appendChild(div);
    }
  })
}

get_reports()
