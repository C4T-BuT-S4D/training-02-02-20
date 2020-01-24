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
  }
};
</script>
