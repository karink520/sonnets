const patristic= require('patristic');
const fs = require('fs');

function make_tree(poets, counts_or_embedding) {
    var input_filename = 'sonnet_dists_' + counts_or_embedding;
    for (i=0; i < poets.length; i++){
        input_filename = input_filename + '_' + poets[i];
    }

    input_filename = input_filename + '.json';
    var output_filename = 'sonnet_tree_' + input_filename.substring(13,)

    var sonnet_names = [];
    if(poets.includes('shakespeare')){
        for (i = 0; i < 154; i++) {
            sonnet_names.push(String(i));
        }
    } 
    if (poets.includes('spenser')){
        for (i = 154; i < 243; i++) {
            sonnet_names.push(String(i));
        }
    }
    if (poets.includes('sidney') ){
        for (i = 243; i < 351; i++) {
            sonnet_names.push(String(i));
        }
    }

    var rawdata = fs.readFileSync(input_filename)
    let dist_mtx = JSON.parse(rawdata);
    var RNJ = patristic.parseMatrix(dist_mtx, sonnet_names);
    var tree = RNJ.toObject()
    jsontree = JSON.stringify(tree);
    fs.writeFileSync(output_filename, jsontree);
}

poets = ['shakespeare', 'spenser', 'sidney']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');

poets = ['shakespeare']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');

poets = ['spenser']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');

poets = ['sidney']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');

poets = ['shakespeare', 'spenser']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');

poets = ['shakespeare', 'sidney']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');

poets = ['spenser', 'sidney']
make_tree(poets, 'counts');
make_tree(poets, 'embedding');



