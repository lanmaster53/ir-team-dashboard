var Dashboard = Vue.component('dashboard', {
    template: `
        <div class="flex flex-col">
            <div v-if="telemetry" class="flex flex-wrap justify-center">
                <team-card v-for="(team, index) in telemetry" v-bind:key="index" v-bind:team="team"></team-card>
            </div>
            <div v-else class="flex flex-wrap justify-center">No data to display.</div>
        </div>
    `,
    data: function() {
        return {
            telemetry: null,
        }
    },
    sockets: {
        log(data) {
            console.log(data);
        },
        newTelemetry(data) {
            if (!this.telemetry) {
                this.telemetry = {}
            }
            if (data.driver.active === true) {
                this.$set(this.telemetry, data.car.id, data)
            }
        },
    },
    created: function() {
        this.$socket.client.open();
    },
    beforeDestroy: function() {
        this.$socket.client.close();
        console.log("Socket disconnected.");
    },
});

Vue.component("team-card", {
    props: {
        team: Object,
    },
    template: `
        <div class="p-2 flex flex-col" style="min-width: 400px;">
            <div class="m-2 px-4 py-2 bg-gray-800 border rounded flex flex-col text-center">
                <div class="mb-2 flex justify-center items-center">
                    <div class="text-lg font-bold">Car #{{ team.car.number }} - {{ team.driver.name }}</div>
                </div>
                <div class="flex">
                    <div class="flex flex-col">
                        <div class="m-2 px-4 py-2 bg-black border rounded flex-grow flex flex-col">
                            <div class="text-md font-bold">Class Position</div>
                            <hr class="m-1">
                            <div><span style="color: gold;">{{ team.car.class_position }} ({{ team.car.class }})</span></div>
                        </div>
                        <div class="m-2 px-4 py-2 bg-black border rounded flex-grow flex flex-col">
                            <div class="text-md font-bold">Incidents</div>
                            <hr class="m-1">
                            <div>Driver: <span style="color: gold;">{{ team.driver.incident_count }}x</span></div>
                            <div>Team: <span style="color: gold;">{{ team.car.incident_count }}x</span></div>
                        </div>
                        <div class="m-2 px-4 py-2 bg-black border rounded flex-grow flex flex-col">
                            <div class="text-md font-bold">Fuel</div>
                            <hr class="m-1">
                            <div>Fuel Remaining: <span style="color: gold;">{{ team.telemetry.fuel_remain }}</span></div>
                            <div>Fuel / Lap: <span style="color: gold;">{{ team.telemetry.fuel_burn_avg }}</span></div>
                            <div>Laps Remaining: <span style="color: gold;">{{ team.telemetry.fuel_laps_remain }}</span></div>
                            <div>Time Remaining:</div>
                            <div><span style="color: gold;">{{ team.telemetry.fuel_time_remain }}</span></div>
                        </div>
                    </div>
                    <div class="flex flex-col">
                        <div class="m-2 px-4 py-2 bg-black border rounded flex-grow flex flex-col">
                            <div class="text-md font-bold">Session</div>
                            <hr class="m-1">
                            <div>Time Remaining:</div>
                            <div><span style="color: gold;">{{ team.session.time_remain }}</span></div>
                            <div><span style="color: gold;">{{ team.telemetry.time_laps_remain }} Laps</span></div>
                        </div>
                        <div class="m-2 px-4 py-2 bg-black border rounded flex-grow flex flex-col">
                            <div class="text-md font-bold">Timing</div>
                            <hr class="m-1">
                            <div>Last Lap Time:</div>
                            <div><span style="color: gold;">{{ team.telemetry.last_lap_time }}</span></div>
                            <div>Average Lap Time:</div>
                            <div><span style="color: gold;">{{ team.telemetry.avg_lap_time }}</span></div>
                            <div>Best Lap Time:</div>
                            <div><span style="color: gold;">{{ team.telemetry.best_lap_time }}</span></div>
                        </div>
                    </div>
                </div>
                <div class="m-2 px-4 py-2 bg-black border rounded flex flex-col">
                    <div class="text-md font-bold">Tires</div>
                    <hr class="m-1">
                    <div class="flex">
                        <div class="flex-grow flex flex-col">
                            <tire-section v-bind:tire="team.telemetry.tire_wear.fl" v-bind:label="'FL'"></tire-section>
                            <tire-section v-bind:tire="team.telemetry.tire_wear.rl" v-bind:label="'RL'"></tire-section>
                        </div>
                        <div class="flex-grow flex flex-col">
                            <tire-section v-bind:tire="team.telemetry.tire_wear.fr" v-bind:label="'FR'"></tire-section>
                            <tire-section v-bind:tire="team.telemetry.tire_wear.rr" v-bind:label="'RR'"></tire-section>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
});

Vue.component("tire-section", {
    props: {
        tire: Array,
        label: String
    },
    template: `
        <div>
            <div>{{ label }}</div>
            <div class="flex justify-center" style="color: gold;">
                <span class="mx-0.5 text-sm" v-for="section in tire">{{ section*100 }}%</span>
            </div>
            <div class="my-2 flex justify-center items-center">
                <tire-model v-for="(wear, index) in tire" v-bind:key="index" v-bind:wear="wear"></tire-model>
            </div>
        </div>
    `
})

Vue.component("tire-model", {
    props: {
        wear: Number,
    },
    template: `
        <div class="w-2 h-6 mx-0.5" v-bind:style="{ backgroundColor: getColorForPercentage(parseFloat(wear)) }"></div>
    `,
    methods: {
        getColorForPercentage: function(pct) {
            for (var i = 1; i < percentColors.length - 1; i++) {
                if (pct < percentColors[i].pct) {
                    break;
                }
            }
            var lower = percentColors[i - 1];
            var upper = percentColors[i];
            var range = upper.pct - lower.pct;
            var rangePct = (pct - lower.pct) / range;
            var pctLower = 1 - rangePct;
            var pctUpper = rangePct;
            var color = {
                r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
                g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
                b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
            };
            return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
            // or output as hex if preferred
        }
    }
});
