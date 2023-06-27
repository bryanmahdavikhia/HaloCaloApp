from django.core.mail import send_mail
from uploadBarang import models as ub_md

# Global
HALO_CALO_EMAIL_STR = 'halocalo.dev@gmail.com'

def send_user_rejected_email(username):
    get_user_object = ub_md.User.objects.get(username=username)
    user_email = get_user_object.email

    subject = 'HaloCalo - Account Verification Rejected'
    body = f"""
Dear {username},

We hope this message finds you well. We are writing to inform you that we have received your account verification documents, but unfortunately, we are unable to verify your account at this time.

Our team has reviewed your documents thoroughly, and while we appreciate your effort in submitting them, we regret to inform you that they did not meet our verification standards. As a result, we are unable to complete the verification process, and your account will remain unverified.

If you have any questions or concerns about this decision, please do not hesitate to reach out to us at halocalo.dev[at]gmail.com.

Best regards,
HaloCalo Team
    """

    from_email = HALO_CALO_EMAIL_STR
    to_email = [f'{user_email}']
    send_mail(subject, body, from_email, to_email, fail_silently=False)

def send_user_accepted_email(username):
    get_user_object = ub_md.User.objects.get(username=username)
    user_email = get_user_object.email

    subject = 'HaloCalo - Account Verification Accepted'
    body = f"""
Dear {username},

We are pleased to inform you that we have received and reviewed your account verification documents, and we would like to thank you for your prompt action in submitting them. We are happy to confirm that your account has been successfully verified, and you can now enjoy all the features and benefits that come with being a verified user.

Our team worked diligently to process your verification as quickly as possible, and we appreciate your cooperation throughout the process. If you have any further questions or concerns, please do not hesitate to reach out to us at halocalo.dev[at]gmail.com.

Thank you for choosing HaloCalo, and we look forward to providing you with excellent service.

Best regards,
HaloCalo Team
    """

    from_email = HALO_CALO_EMAIL_STR
    to_email = [f'{user_email}']
    send_mail(subject, body, from_email, to_email, fail_silently=False)

def send_listing_rejected_email(listing_id):
    get_listing_object = ub_md.Listing.objects.get(id=listing_id)
    listing_seller = get_listing_object.seller_username
    
    get_user_object = ub_md.User.objects.get(username=listing_seller)
    user_email = get_user_object.email
    user_username = get_user_object.username

    subject = 'HaloCalo - Listing Document Rejected'
    body = f"""
Dear {user_username},

We would like to take this opportunity to thank you for choosing our platform to list your item. We are writing to confirm that we have received your listing documents, and we appreciate your prompt action in submitting them. Thank you for your cooperation in this matter.

Our team has thoroughly reviewed your documents and unfortunately, we regret to inform you that your listing has been rejected. We have determined that your item does not meet our platform's standards and guidelines, and therefore, we cannot proceed with listing it.

We understand that this may come as disappointing news, but please note that our decision was made to ensure that our platform maintains its reputation for offering high-quality and reliable items to potential buyers.

If you have any questions or concerns about our decision or would like more information about why your listing was rejected, please do not hesitate to reach out to us at halocalo.dev[at]gmail.com.

Thank you for choosing our platform, and we wish you all the best in your future endeavors.

Best regards,
HaloCalo Team
    """

    from_email = HALO_CALO_EMAIL_STR
    to_email = [f'{user_email}']
    send_mail(subject, body, from_email, to_email, fail_silently=False)

def send_listing_accepted_email(listing_id):
    get_listing_object = ub_md.Listing.objects.get(id=listing_id)
    listing_seller = get_listing_object.seller_username

    get_user_object = ub_md.User.objects.get(username=listing_seller)
    user_email = get_user_object.email
    user_username = get_user_object.username

    subject = 'HaloCalo - Listing Document Accepted'
    body = f"""
Dear {user_username},

We would like to extend our sincerest congratulations on successfully listing your item on our platform. We are writing to confirm that we have received your listing documents, and we appreciate your prompt action in submitting them. Thank you for your cooperation in this matter.

Our team has thoroughly reviewed your documents and is pleased to inform you that your listing has been accepted and processed successfully. You can now view your item on our platform through the following URL: http://20.5.202.87/listing/{listing_id}.

Rest assured that we will continue to provide our support in ensuring that your item gains maximum exposure and generates interest from potential buyers.

If you have any questions or concerns, please do not hesitate to reach out to us at halocalo.dev[at]gmail.com.

Once again, congratulations on listing your item with us, and we wish you all the best in your future endeavors.

Best regards,
HaloCalo Team
    """

    from_email = HALO_CALO_EMAIL_STR
    to_email = [f'{user_email}']
    send_mail(subject, body, from_email, to_email, fail_silently=False)