			//================================================================
  				//======= ajax call to subscribe petjibe community
  			//================================================================
			$("#subscribe").on("click",function(e){
				e.preventDefault();
				var subscribe_email = $("#subEmail").val();
				data={
						"subscribe_email":subscribe_email
				}
				$.ajax({
					type:'POST',
					url:'/email_subscription/',
					data:data,
					error:function(e){alert('error');},
					success:function(data){//alert(data['message']);	
						$("#subEmail").val("");
						$("#msgSub").text("Your email has been sent.Thank you for subscribing petjibe!");
					},
					headers:{"X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').attr('value')},
				});
			});
			
			//========================================================
				//==== ajax call to submit contact form
			//========================================================
			$("#cntform").on("submit",function(e){
				var cname = $("#cname").val();
				var cemail = $("#cemail").val();
				var csubject=$("#csubject").val();
				var cmessage=$("#cmessage").val();
				
				data = {
						"cname":cname,
						"cemail":cemail,
						"csubject":csubject,
						"cmessage":cmessage
					}
				
				$.ajax({
					type:'POST',
					url:'/contactus/',
					data:data,
					error:function(e){alert('error');},
					success:function(data){//alert(data['msg']);	
						$("#cname").val("");
						$("#cemail").val("");
						$("#csubject").val("");
						$("#cmessage").val("");
						$("#msg").text("Your mesage has been sent.Thank you!");							
					},
					headers:{"X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').attr('value')},
				});
				
			});