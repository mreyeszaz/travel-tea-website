/ This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
        
    };

    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            // Only user's post are going to be editable so we need to check 
            if(p.email == user_email) {
                p.editable = true;
            } else {
                p.editable = false;
            }
            
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
        }
        return a;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of app.vue.posts) {
            p._idx = i++;
        }
    };

    app.do_edit = (post_idx) => {
        // Function for edit feature 
        // Need to make sure that no other post is being or can be edited.
        // If so, do nothing.  
        //Otherwise, proceed as below.

        ///this would be if we wanted to edit ONE at a time ONLY
        // for(let i = 0; i < app.data.posts.length; i++) {
        //     if(app.data.posts[i].edit == true) {
        //         return
        //     }
        // }


        let p = app.vue.posts[post_idx];
        p.edit = true;
        p.is_pending = false;
    };

    app.do_cancel = (post_idx) => {
        // Handler for button that cancels the edit.
        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // If the post has not been saved yet, we delete it.
            app.vue.posts.splice(post_idx, 1);
            app.reindex();
        } else {
            // We go back to before the edit.
            p.edit = false;
            p.is_pending = false;
            p.content = p.original_content;
        }
    }

    app.do_save = (post_idx) => {
        // Handler for "Save edit" button.
        let p = app.vue.posts[post_idx];
        if (p.content !== p.server_content) {
            p.is_pending = true;
            axios.post(posts_url, {
                content: p.content,
                id: p.id,
                is_reply: p.is_reply,
            }).then((result) => {
                console.log("Received:", result.data);
                p.id = result.data.id
                p.edit = false
                p.is_pending = false
                // TODO: You are receiving the post id (in case it was inserted),
                // and the content.  You need to set both, and to say that
                // the editing has terminated.
            }).catch(() => {
                p.is_pending = false;
                console.log("Caught error");
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;
            p.original_content = p.content;
        }


    }

    app.add_post = () => {
        // Function:  Inserting a new post.
        // First, need to initialize below->
        let new_post = {
            id: null,
            edit: true,
            editable: true,
            content: "",
            server_content: null,
            original_content: "",
            user: user_name,
            email: user_email,
            is_reply: null,
            
        };

        //Insert post at the top the list 
        app.data.posts = [new_post, ...app.data.posts]
        app.reindex(); // reenumerate roe with reindex
        
        // should print into console 
        console.log("Add post")
    };

    app.reply = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id !== null) {
            // A new reply.  Need to initialize it!
            let init_reply = {
                id: null,
                edit: true,
                editable: true,
                content: "",
                server_content: null,
                original_content: "",
                user: user_name,
                email: user_email,
                is_reply: p.id,
            };

            // organized_posts = []
            // for post in p:
            //     if (post.is_reply == null):
            //         organized_posts.append(mainPost = [])
            //     else:
            //         organized_posts[post].append(post)

            reply_list = []
            for(let k = 0; k < app.data.posts.length; k++) {
                reply_list.push(app.data.posts[k]) // should push app.data.post[k] to reply_list
                if(k == post_idx) {
                    reply_list.push(init_reply)
                }
            }

            app.data.posts = reply_list
            app.reindex()

            console.log("Reply to post")

            // TODO: and you need to insert it in the right place, and reindex
            // the posts.  Look at the code for app.add_post; it is similar.
        }
    };

    app.do_delete = (post_idx) => {
        let p = app.vue.posts[post_idx];
        
        if (p.id === null) {
            // TODO:
            // If the post has never been added to the server,
            // simply deletes it from the list of posts.
            app.data.posts.splice(post_idx, 1)
            app.reindex()
        } else {
            // TODO: Deletes it on the server.
            // app.data.posts.splice(post_idx, 1)
            //from hw5
            axios.post(delete_url, {id: p.id}).then((response) => {
            // The deletion went through on the server. Deletes also locally.
            // Isn't it obvious that splice deletes an element?  Such is life.
            
                app.vue.posts.splice(post_idx, 1);
                app.reindex();
            })
        }
    };

    //change_thumb(): Function to set the thumb rating
    //DEFINE:
    //thumb_choice is either 0 (up) or 1 (down) when rating
    app.change_thumb = (post_idx, thumb_choice) => { 
        let post = app.vue.posts[post_idx];
        let thumb_rating = 0; 
        // Change thumb_rating to represent the 3 states of thumb rating up/down
        //diff cases listed below 
        if(post.rating === 0) { //both thumb up and down are opaque 
            if(thumb_choice === 0) thumb_rating = 1; // thumb up is clicked
            else thumb_rating = 2; // thumb down is clicked
        }else if (post.rating === 1){ // only thumb down is opaque
            if(thumb_choice === 0) thumb_rating = 0;
            else thumb_rating = 2;
        }else{ // only thumb up is opaque
            if(thumb_choice === 0) thumb_rating = 1;
            else thumb_rating = 0;
        }
        axios.post(set_thumb_url, {post_id: post.id, rating: thumb_rating});
        app.vue.check_change_thumb_liked = true; // If we select thumbs up
        app.vue.check_change_thumb_disliked = true; // If we select thumbs down
        app.thumb_over(post_idx, thumb_rating);
        post.rating = thumb_rating;
    };

    app.thumb_out = (post_idx) => {
        let post = app.vue.posts[post_idx];
        post.show_liked_users = false;
        post.show_disliked_users = false;
    };



    app.thumb_over = (post_idx, thumb_choice) => {
        let post = app.vue.posts[post_idx];
        //If first hovering over post, want to use get_thumb
        if(post.asleep === true){
            app.vue.check_change_thumb_liked = post.asleep;
            app.vue.check_change_thumb_disliked = post.asleep;
            post.asleep = false; // Wake up post so that it obeys check_change_thumb rules below afterwards
        }

        // Show everyone who placed the thumb rating
        if(thumb_choice === 1){ //Show all who LIKED post
            if(app.vue.check_change_thumb_liked === true){ // use axios.get only change_thumb
                app.vue.check_change_thumb_liked = false;
                axios.get(get_thumb_url, {params: {"post_id": post.id, "rating": thumb_choice}})
                    .then((result) => {
                        post.display_liked_users = result.data.s;
                        if(post.display_liked_users != ""){
                            post.show_liked_users = true; //Need this here because you want to show liked users AFTER get_thumb finishes
                        }
                    });
            }
            //Goes through even if thumb rating has not changed
            else if (post.display_liked_users !== ""){ // Don't display empty string
                post.show_liked_users = true;
            }
        }
        if(thumb_choice === 2){ //Show all who DISLIKED post
            if(app.vue.check_change_thumb_disliked === true){
                app.vue.check_change_thumb_disliked = false;
                axios.get(get_thumb_url, {params: {"post_id": post.id, "rating": thumb_choice}})
                    .then((result) => {
                        post.display_disliked_users = result.data.s;
                        if(post.display_disliked_users != ""){
                            post.show_disliked_users = true;
                        }
                    });
            }
            else if (post.display_disliked_users !== ""){ //Check if no users have disliked post
                post.show_disliked_users = true;
            }
        }
    };
    
    



    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
        // should deal with like and dislikes hopefully
        change_thumb: app.change_thumb,
        thumb_over: app.thumb_over,
        thumb_out: app.thumb_out,
       
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // You should load the posts from the server.



        // Load the posts from the server instead.
        //  Then We set the posts later here.
        axios.get(posts_url).then((result) => {

            let posts = result.data.posts
            
            app.vue.posts = app.index(posts);
            posts.map((post) => {
                // alerts Vue to a new attribute of post
                //should set rating to originally be 0
                Vue.set(post, "rating", 0);
            })
        }).then(() => {

            for(let post of app.vue.posts){
                axios.get(get_rating_url, {params: {"post_id": post.id}})
                    .then((result) => {
                        Vue.set(post, "rating", result.data.rating);
                     });
            } 
    });
    console.log("app.init called...")

        // app.vue.posts = app.index(posts);
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
