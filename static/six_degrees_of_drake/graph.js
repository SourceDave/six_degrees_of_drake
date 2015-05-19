// GRAPH.JS REQUIRES:
// JQUERY
// D3JS

var WIDTH = 500,
    HEIGHT = 500,
    NODE_RADIUS = 32,
    IMAGE_URL = "{% static 'six_degrees_of_drake/unknown.jpg' %}",
    STROKE = "#0095dd",
    STROKE_WIDTH = "2px",
    STROKE_OPACITY = ".6";

var color = d3.scale.category10();

var nodes = [],
    links = [];

var force = d3.layout.force()
    .nodes(nodes)
    .links(links)
    .linkDistance(120)
    .charge(-400)
    .size([WIDTH, HEIGHT])
    .on("tick", tick);

var svg = d3.select("body").append("svg")
    .attr("width", WIDTH)
    .attr("height", HEIGHT);

var imageDefinitions = svg.append("defs").attr("id", "img-defs");

var node = svg.selectAll(".node"),
    link = svg.selectAll(".link");

function addLink(id1, id2, weight) {
    var node1 = $.grep(nodes, function(n) { return n.id === id1; })[0];
    var node2 = $.grep(nodes, function(n) { return n.id === id2; })[0];
    links.push({source: node1, target: node2, weight: 30});
    start();
}

function addNode(id, name, imageUrl) {
    imageUrl = imageUrl || IMAGE_URL;
    n = {id:id, name:name, imageUrl:imageUrl};
    nodes.push(n);

    var nodePattern = imageDefinitions.append("pattern")
        .attr("id", "lol")
        .attr("height", 1)
        .attr("width", 1)
        .attr("x", "0")
        .attr("y", "0");

    nodePattern.append("image")
        .attr("height", NODE_RADIUS*2)
        .attr("width", NODE_RADIUS*2)
        .attr("xlink:href", imageUrl);

    start();
}

function start() {
    link = link.data(force.links(), function(d) { return d.source.id + "-" + d.target.id; });
    link.enter().insert("line", ".node")
        .attr("stroke", STROKE)
        .attr("stroke-width", STROKE_WIDTH)
        .attr("stroke-opacity", STROKE_OPACITY)
        .attr("class", "link");
    link.exit().remove();

    node = node.data(force.nodes(), function(d) { return d.id;});
    node.enter().append("circle")
        .attr("r", NODE_RADIUS)
        .attr("stroke", STROKE)
        .attr("stroke-width", STROKE_WIDTH)
        .attr("stroke-opacity", STROKE_OPACITY)
        .attr("class", function(d) { return "node " + d.id; })
        .attr("fill", function(d) { return "url(#lol)"; })
        .call(force.drag);
    node.exit().remove();

    force.start();
}

function tick() {
    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })

        link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
}

// Add sample nodes. Delete later
addNode('1', 'name1');
addNode('2', 'name2');
addNode('3', 'name3');

addLink('1', '2');
addLink('3', '2');
addLink('1', '3');
