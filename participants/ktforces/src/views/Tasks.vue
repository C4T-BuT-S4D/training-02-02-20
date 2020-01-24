<template>
  <div v-if="requested">
    <v-pagination v-model="page" :length="maxpage" total-visible="6" />
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      requested: false,
      page: 1,
      maxpage: 1
    };
  },

  created: async function() {
    const { page = 0 } = this.$route.query;
    const r = await this.$http.get(`/tasks/?limit=5&offset=${page * 5}`);
    console.log(r);
  }
};
</script>
