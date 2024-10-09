import base64
from django.apps import apps
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import Event, FormConfig
from .forms import create_dynamic_form
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def index(request):
    # return HttpResponse("This is a function based view.")
    context = {
        'key' : 'value'
    }
    return render(request,'index.html',context)

def contact(request):
    return render(request,'contact.html')

def events(request):
    upcoming_events = Event.objects.filter(isDone=False).order_by('date')
    completed_events = Event.objects.filter(isDone=True).order_by('-date')
    return render(request, 'events.html', {
        'upcoming_events': upcoming_events,
        'completed_events': completed_events,
    })

def event_info(request, event_id):
    event = Event.objects.get(id=event_id) 
    return render(request, 'event_info.html', {'event': event})

def sucess(request):
    return render(request, 'sucess.html')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, FormConfig, Ticket
from .forms import create_dynamic_form

def register_event(request, event_id, form_id):
    # Fetch the event and form configuration
    event = get_object_or_404(Event, id=event_id)
    form_config = get_object_or_404(FormConfig, id=form_id)
    FORM_CONFIGS = form_config.fields  

    # Create the dynamic form
    DynamicForm = create_dynamic_form(form_id)

    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES) 
        if form.is_valid():
            # Handle the form submission
            submitted_data = form.cleaned_data

            # Initialize variables for uploaded file
            uploaded_file = None
            file_field_name = None

            # Iterate through fields in the form configuration
            for field in FORM_CONFIGS['fields']:
                if field['type'] == 'image' or field['type'] == 'file':  # Check for file/image type
                    file_field_name = field['name']  # Get the name of the file field
                    uploaded_file = request.FILES.get(file_field_name)  # Retrieve the uploaded file

            # Create a unique ticket ID
            ticket_id = f"evt_{event_id}_tk_{Ticket.objects.count() + 1}"
            
            #encryption of ticket_id
            byte_string = ticket_id.encode('utf-8')
            base64_bytes = base64.b64encode(byte_string)
            enc_tk_id = base64_bytes.decode('utf-8')

            # Save the form data (excluding the file) and event reference to the Ticket model
            Ticket.objects.create(
                ticket_id=ticket_id,
                enc_tk_id = f"www.valid-entry.in/tk/{enc_tk_id}",
                event_id=event,  # Save the reference to the event
                ticket_data={k: v for k, v in submitted_data.items() if k != file_field_name},  # Exclude the file data from JSON
                uploaded_file=uploaded_file  # Save the file to FileField
            )

            # Redirect to a success page or render success message
            return render(request, 'sucess.html', {
                'submitted_data': submitted_data,
                'ticket_id': ticket_id,  # Include ticket_id here
            })

    else:
        form = DynamicForm()  # Initialize the form for GET requests

    return render(request, 'register_event.html', 
                  {'event': event, 
                   'form': form, 
                   'title': FORM_CONFIGS['title'], 
                   'form_id': form_id,
                   'event_form_id': event.form_id })


import os

def download_ticket(request, ticket_id):
    # Fetch the Ticket object
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    event = ticket.event_id  # Get the associated event
    enc_tk_id = ticket.enc_tk_id

    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(enc_tk_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Create a blank ticket image
    ticket_image = Image.open('static/ticket.jpg')
    draw = ImageDraw.Draw(ticket_image)

    # Define fonts (you may need to adjust the font path)
    title_font = ImageFont.load_default(size=20)
    detail_font = ImageFont.load_default()

    center_x, center_y = 150, 100 
    event_text = f"Event: {event.title}"
    bbox = draw.textbbox((0, 0), event_text, font=title_font)
    text_width = bbox[2] - bbox[0]  # Calculate width from the bounding box
    x_position = center_x - (text_width // 2)

    # Draw event name and QR code on the ticket image
    draw.text((x_position, center_y), event_text, fill="white", font=title_font)
    draw.text((125, 425), f"{ticket_id}", fill="black", font=detail_font)

    # Resize QR code and paste it onto the ticket image
    qr_img = qr_img.resize((170, 170))
    ticket_image.paste(qr_img, (65, 150))  # Adjust position as needed

    # Define a path to save the ticket image
    ticket_image_path = f'media/tickets/{ticket_id}.png'
    ticket_image.save(ticket_image_path, format='PNG')

    # Return the image as an HTTP response for downloading
    with open(ticket_image_path, 'rb') as img_file:
        response = HttpResponse(img_file.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{ticket_id}.png"'
        return response
