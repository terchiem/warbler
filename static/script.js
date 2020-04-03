$(async function() {  
  let $likeButtons = $('.like-btn');
  $likeButtons.on('click', handleLikeClick);


  async function handleLikeClick(evt) {
    evt.preventDefault();

    let messageId = evt.currentTarget.id;

    // make a post request to like route
    let response = await axios.post(`/api/messages/${messageId}/like`);

    // update button appearance
    let $currentBtn = $(evt.currentTarget);
    $currentBtn.toggleClass("btn-primary btn-secondary");

    // remove message from list if on liked messages list
    let $likeList = $('.like-list');
    if($likeList.length) {
      $currentMessage = $(`#liked-message-${messageId}`);
      $currentMessage.remove();
    }
  }
})