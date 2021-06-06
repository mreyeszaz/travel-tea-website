// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        query: "",
        country_results: [],
        post_results: [],
        results: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.set_type = (a, type) => {
        a.map((item) => {item.type = type;});
        return a;
    };

    app.sort_results = () => {
        app.vue.country_results = app.set_type(app.vue.country_results, "country");
        app.vue.post_results = app.set_type(app.vue.post_results, "post");
        app.vue.results = app.vue.post_results.concat(app.vue.country_results);
        app.vue.results.sort();
    };

    app.search = function () {
        if (app.vue.query.length > 1) {
            axios.get(search_url, {params: {q: app.vue.query}})
                .then(function (result) {
                    app.vue.country_results = (result.data.country_results);
                    app.vue.post_results = (result.data.post_results);
                    app.sort_results();
                });
        } else {
            app.vue.results = [];
        }
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        app.vue.query = "";
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
