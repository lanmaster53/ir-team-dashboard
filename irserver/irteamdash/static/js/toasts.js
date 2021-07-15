Vue.component("toasts", {
    template: `
        <div class="fixed top-4 right-6 z-10 flex flex-col items-end">
            <toast v-for="toast in toasts" v-bind:key="toast.id" v-bind:toast="toast"></toast>
        </div>
    `,
    computed: {
        toasts: function() {
            return store.getters.getToasts;
        }
    },
});

Vue.component("toast", {
    props: {
        toast: Object,
    },
    template: `
        <div class="mb-2 py-2 px-3 rounded shadow-md" v-bind:class="levelClass" v-bind:style="{ zIndex: 100-toast.id }">{{ toast.content }}</div>
    `,
    computed: {
        levelClass: function() {
            switch(this.toast.level) {
                case "INFO":
                    return "bg-green-600";
                case "WARN":
                    return "bg-blue-600";
                case "ERROR":
                    return "bg-red-600";
                default:
                    // default to ERROR level
                    return "bg-red-600";
            }
        }
    },
});
