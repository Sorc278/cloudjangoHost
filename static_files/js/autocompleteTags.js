var awe;

function autocompleteInit(url, inputName){
    var tags;
    $.getJSON(url,
        function(data){
            tags = $.map(data, function(el) { return el })
            awe = new Awesomplete(document.getElementById(inputName), {filter: Awesomplete.FILTER_STARTSWITH,
        		data: function (text, input) {
        			var indexStart = Math.max(input.lastIndexOf(" "), input.lastIndexOf("-"));
        			return input.slice(0, indexStart+1) + text;
        		},
        		autoFirst: true,
        		list: tags}
        	);
        	document.getElementById(inputName).focus();
        }
    );
}