//
//  TaskDetailsController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskDetailsController.h"
#import "DatePickerViewController.h"
#import "TaskCategoryPickerController.h"

#import "Task.h"

#import "CellFactory.h"
#import "TextFieldCell.h"
#import "DescriptionCell.h"

#import "DateUtils.h"
#import "Database.h"
#import "Statement.h"
#import "i18n.h"

//======================================================================

@implementation TaskDetailsController

- (void)updateTrackButton
{
	BOOL isTracking = [task startTimeOfCurrentEffort] != nil;

	UIImage *img;

	if (isTracking)
	{
		img = [[UIImage imageNamed:@"blueButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	}
	else
	{
		img = [[UIImage imageNamed:@"redButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	}

	[effortCell.button setBackgroundImage:img forState:UIControlStateNormal];

	img = [[UIImage imageNamed:@"whiteButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	[effortCell.button setBackgroundImage:img forState:UIControlStateHighlighted];

	if (isTracking)
		[effortCell.button setTitle:_("Stop tracking") forState:UIControlStateNormal];
	else
		[effortCell.button setTitle:_("Start tracking") forState:UIControlStateNormal];
}

- initWithTask:(Task *)theTask category:(NSInteger)category
{
	if (self = [super initWithNibName:@"TaskDetails" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		categoryId = category;

		cells = [[NSMutableArray alloc] initWithCapacity:5];

		effortCell = [[CellFactory cellFactory] createButtonCell];
		[self updateTrackButton];
		[effortCell.button setTitleColor:[UIColor blackColor] forState:UIControlStateNormal];
		[effortCell setTarget:self action:@selector(onTrack:)];
		[cells addObject:effortCell];

		TextFieldCell *nameCell = [[CellFactory cellFactory] createTextFieldCell];
		nameCell.textField.delegate = self;
		nameCell.textField.text = task.name;
		[cells addObject:nameCell];
		
		descriptionCell = [[CellFactory cellFactory] createDescriptionCell];
		descriptionCell.textView.delegate = self;
		descriptionCell.textView.text = task.description;
		[cells addObject:descriptionCell];
		
		categoriesCell = [[UITableViewCell alloc] initWithFrame:CGRectZero];
#ifdef __IPHONE_3_0
		categoriesCell.textLabel.text = 
#else
		categoriesCell.text = 
#endif
		    _("Categories");

		categoriesCell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
		[cells addObject:categoriesCell];
		[categoriesCell release];

		startDateCell = [[CellFactory cellFactory] createDateCell];
		[startDateCell setDelegate:self];
		startDateCell.label.text = _("Start");
		[startDateCell setDate:task.startDate];
		[cells addObject:startDateCell];
		
		dueDateCell = [[CellFactory cellFactory] createDateCell];
		[dueDateCell setDelegate:self];
		dueDateCell.label.text = _("Due");
		[dueDateCell setDate:task.dueDate];
		[cells addObject:dueDateCell];
		
		completionDateCell = [[CellFactory cellFactory] createDateCell];
		[completionDateCell setDelegate:self];
		completionDateCell.label.text = _("Completion");
		[completionDateCell setDate:task.completionDate];
		[cells addObject:completionDateCell];
	}

	return self;
}

- (void)dealloc
{
	[task release];
	[cells release];

	[super dealloc];
}

- (void)saveTask
{
	BOOL isNew = (task.objectId == -1);
	[task save];
	
	if (isNew && (categoryId != -1))
	{
		Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO TaskHasCategory (idTask, idCategory) VALUES (?, ?)"];
		[req bindInteger:task.objectId atIndex:1];
		[req bindInteger:categoryId atIndex:2];
		[req exec];
	}
}

- (void)viewDidLoad
{
	if (task.objectId == -1)
	{
		// New task.
		TextFieldCell *cell = [cells objectAtIndex:1];
		[cell.textField becomeFirstResponder];
		self.navigationItem.title = _("New task");
	}
	else
	{
		self.navigationItem.title = task.name;
	}
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	if ((toInterfaceOrientation == UIInterfaceOrientationLandscapeLeft) || (toInterfaceOrientation == UIInterfaceOrientationLandscapeRight))
		self.navigationItem.hidesBackButton = YES;

	return YES;
}

- (void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation
{
	if ([UIDevice currentDevice].orientation == UIInterfaceOrientationPortrait)
		self.navigationItem.hidesBackButton = NO;
}

- (void)onSwitchValueChanged:(SwitchCell *)cell
{
	if (cell == startDateCell)
	{
		if (cell.switch_.on)
		{
			DatePickerViewController *ctrl = [[DatePickerViewController alloc] initWithDate:task.startDate target:self action:@selector(onPickStartDate:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			task.startDate = nil;
			[self saveTask];
			[startDateCell setDate:nil];
		}
	}
	else if (cell == dueDateCell)
	{
		if (cell.switch_.on)
		{
			NSString *date = nil;

			if (task.dueDate)
				date = task.dueDate;
			else if (task.startDate)
				date = task.startDate;

			DatePickerViewController *ctrl = [[DatePickerViewController alloc] initWithDate:date target:self action:@selector(onPickDueDate:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			task.dueDate = nil;
			[self saveTask];
			[dueDateCell setDate:nil];
		}
	}
	else if (cell == completionDateCell)
	{
		if (cell.switch_.on)
		{
			DatePickerViewController *ctrl = [[DatePickerViewController alloc] initWithDate:task.completionDate target:self action:@selector(onPickCompletionDate:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			task.completionDate = nil;
			[self saveTask];
			[completionDateCell setDate:nil];
		}
	}
}

- (void)onPickStartDate:(NSDate *)date
{
	[self.navigationController dismissModalViewControllerAnimated:YES];
	
	if (date)
	{
		task.startDate = [[DateUtils instance] stringFromDate:date];
		
		if (task.dueDate)
		{
			NSDate *dueDate = [[DateUtils instance] dateFromString:task.dueDate];
			if ([dueDate compare:date] == NSOrderedAscending)
			{
				task.dueDate = task.startDate;
			}
		}
	}
	else if (!task.startDate)
	{
		[startDateCell.switch_ setOn:NO animated:YES];
	}
	
	[self saveTask];
	
	[startDateCell setDate:task.startDate];
	[dueDateCell setDate:task.dueDate];
}

- (void)onPickDueDate:(NSDate *)date
{
	[self.navigationController dismissModalViewControllerAnimated:YES];
	
	if (date)
	{
		task.dueDate = [[DateUtils instance] stringFromDate:date];
		
		if (task.startDate)
		{
			NSDate *startDate = [[DateUtils instance] dateFromString:task.startDate];
			if ([startDate compare:date] == NSOrderedDescending)
			{
				task.startDate = task.dueDate;
			}
		}
	}
	else if (!task.dueDate)
	{
		[dueDateCell.switch_ setOn:NO animated:YES];
	}
	
	[self saveTask];

	[startDateCell setDate:task.startDate];
	[dueDateCell setDate:task.dueDate];
}

- (void)onPickCompletionDate:(NSDate *)date
{
	[self.navigationController dismissModalViewControllerAnimated:YES];

	if (date)
		task.completionDate = [[DateUtils instance] stringFromDate:date];
	else
		task.completionDate = nil;

	[self saveTask];
	[completionDateCell setDate:task.completionDate];
}

- (void)onTrack:(ButtonCell *)cell
{
	if ([task startTimeOfCurrentEffort])
	{
		[task stopTracking];
	}
	else
	{
		[task startTracking];
	}

	[self updateTrackButton];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	return @"";
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	return [cells count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return [cells objectAtIndex:indexPath.row];
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell = [cells objectAtIndex:indexPath.row];
	UIViewController *ctrl = nil;

	if (cell == categoriesCell)
	{
		TaskCategoryPickerController *categoryPicker = [[TaskCategoryPickerController alloc] initWithTask:task];
		[self.navigationController pushViewController:categoryPicker animated:YES];
		[categoryPicker release];
	}
	else if (cell == startDateCell)
	{
		ctrl = [[DatePickerViewController alloc] initWithDate:task.startDate target:self action:@selector(onPickStartDate:)];
	}
	else if (cell == dueDateCell)
	{
		ctrl = [[DatePickerViewController alloc] initWithDate:task.dueDate target:self action:@selector(onPickDueDate:)];
	}
	else if (cell == completionDateCell)
	{
		ctrl = [[DatePickerViewController alloc] initWithDate:task.completionDate target:self action:@selector(onPickCompletionDate:)];
	}

	if (ctrl)
	{
		[self.navigationController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell = [cells objectAtIndex:indexPath.row];
	
	if (cell == descriptionCell)
		return 150;
	return 44;
}

#pragma mark UITextFieldDelegate protocol

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[textField resignFirstResponder];
	return NO;
}

- (void)textFieldDidEndEditing:(UITextField *)textField
{
	if ([textField.text length])
	{
		task.name = textField.text;
	}
	else
	{
		task.name = _("New task");
		textField.text = task.name;
	}

	[self saveTask];
	self.navigationItem.title = task.name;
}

#pragma mark UITextViewDelegate protocol

- (BOOL)textViewShouldBeginEditing:(UITextView *)textView
{
	UIBarButtonItem *button = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemSave target:self action:@selector(onSaveDescription:)];
	self.navigationItem.rightBarButtonItem = button;
	[button release];
	
	return YES;
}

- (void)textViewDidEndEditing:(UITextView *)textView
{
	self.navigationItem.rightBarButtonItem = nil;
	task.description = descriptionCell.textView.text;
	[self saveTask];
}

- (void)onSaveDescription:(UIBarButtonItem *)button
{
	[descriptionCell.textView resignFirstResponder];
}

@end

