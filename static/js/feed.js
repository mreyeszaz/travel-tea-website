// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete.
        add_mode: false,
        comment_list: [],
        new_comment: "",
    };

    app.add_comment = function () {
        app.vue.comment_list.unshift(app.vue.new_comment);
        app.vue.new_comment = "";
        app.set_add_status(false);
    };

    app.cancel_comment = function () {
        app.vue.new_comment = "";
        app.set_add_status(false);
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.methods = {
        // Complete.
        add_comment: app.add_comment,
        cancel_comment: app.cancel_comment,
        set_add_status: app.set_add_status,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Do any initializations (e.g. networks calls) here.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
